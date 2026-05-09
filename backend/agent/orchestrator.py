"""Main agent loop — orchestrates LLM + tools + permissions."""
import json
import re
from backend.services.llm_router import llm_router
from backend.automation.actions import execute_action, ACTION_REGISTRY
from backend.agent.tools import SYSTEM_PROMPT, TOOL_DEFINITIONS, build_tool_call_instructions
from backend.agent.permissions import needs_approval, request_approval
from backend.models.agent import ChatRequest, ChatResponse, AgentStatus
from backend.models.action import PendingApproval
from backend.config import settings
from backend.utils.logger import get_logger

logger = get_logger(__name__)

# Global agent status (single-user desktop app)
_agent_status = AgentStatus(status="idle")


def get_agent_status() -> AgentStatus:
    return _agent_status


def _set_status(status: str, task: str | None = None, model: str | None = None, session: str | None = None):
    _agent_status.status = status  # type: ignore
    _agent_status.current_task = task
    if model:
        _agent_status.model = model
    if session:
        _agent_status.session_id = session


def _extract_tool_call(text: str) -> dict | None:
    """Parse JSON tool call from model output if present."""
    # Try to find JSON block in the response
    match = re.search(r'\{[^{}]*"tool"[^{}]*\}', text, re.DOTALL)
    if match:
        try:
            data = json.loads(match.group())
            if "tool" in data:
                return data
        except json.JSONDecodeError:
            pass

    # Try full response as JSON
    try:
        data = json.loads(text.strip())
        if "tool" in data:
            return data
    except json.JSONDecodeError:
        pass

    return None


async def process_chat(request: ChatRequest) -> ChatResponse:
    """Process a chat request through the agent loop."""
    _set_status("thinking", request.message[:80], session=request.session_id)

    messages: list[dict] = []
    actions_taken: list[dict] = []
    pending_approvals: list[dict] = []

    # Build system prompt with tool instructions for local models
    tool_instructions = build_tool_call_instructions(TOOL_DEFINITIONS)
    system = f"{SYSTEM_PROMPT}\n\n{tool_instructions}"
    messages.append({"role": "system", "content": system})

    # Add user message
    user_content = request.message
    if request.attachments:
        parts = [user_content]
        for att in request.attachments:
            if att.type == "text":
                parts.append(f"\n[Attached text: {att.name}]\n{att.content}")
            elif att.type in ("image", "screenshot"):
                parts.append(f"\n[Attached image: {att.name}]")
        user_content = "\n".join(parts)

    messages.append({"role": "user", "content": user_content})

    images = [
        att.content for att in request.attachments
        if att.type in ("image", "screenshot")
    ]

    # Agentic loop (max 5 tool calls)
    final_response = ""
    model_used = ""

    for iteration in range(5):
        try:
            raw_response, model_used = await llm_router.chat(
                messages=messages,
                model=request.model,
                images=images if iteration == 0 else None,
            )
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            _set_status("error")
            return ChatResponse(
                session_id=request.session_id,
                message=f"Error: {e}",
                model_used="unknown",
                actions_taken=actions_taken,
                pending_approvals=pending_approvals,
            )

        tool_call = _extract_tool_call(raw_response)

        if not tool_call:
            final_response = raw_response
            break

        action_name = tool_call.get("tool", "")
        parameters = tool_call.get("parameters", {})

        _set_status("acting", f"Running: {action_name}", model=model_used)

        if not request.allow_actions or settings.safe_mode:
            # In safe mode, describe but don't execute
            tool_result = f"[SAFE MODE] Would run: {action_name}({parameters})"
        elif needs_approval(action_name, request.session_id):
            approval = request_approval(action_name, parameters)
            pending_approvals.append(approval.model_dump())
            tool_result = f"[Waiting for approval to run {action_name}]"
            # Stop the loop — user must approve before continuing
            final_response = f"I need your approval to {approval.description}. Please approve or deny the pending action."
            break
        else:
            result = await execute_action(action_name, parameters, dry_run=settings.dry_run_mode)
            tool_result = json.dumps(result.output) if result.output is not None else result.error or "Done"
            actions_taken.append({
                "action": action_name,
                "parameters": parameters,
                "success": result.success,
                "output_summary": str(tool_result)[:200],
            })

        messages.append({"role": "assistant", "content": raw_response})
        messages.append({"role": "user", "content": f"Tool result for {action_name}: {tool_result}"})

    _set_status("idle", model=model_used, session=request.session_id)

    return ChatResponse(
        session_id=request.session_id,
        message=final_response,
        model_used=model_used,
        actions_taken=actions_taken,
        pending_approvals=pending_approvals,
    )
