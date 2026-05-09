from fastapi import APIRouter, HTTPException
from backend.models.action import ActionRequest, ActionResult, ApprovalDecision, PendingApproval
from backend.automation.actions import execute_action, ACTION_REGISTRY
from backend.agent.permissions import (
    get_pending_approvals, resolve_approval, needs_approval, request_approval
)
from backend.config import settings

router = APIRouter(prefix="/actions", tags=["actions"])


@router.get("/list")
async def list_actions():
    return [a.model_dump() for a in ACTION_REGISTRY.values()]


@router.post("/execute", response_model=ActionResult)
async def execute(req: ActionRequest):
    if req.action_name not in ACTION_REGISTRY:
        raise HTTPException(status_code=404, detail=f"Action '{req.action_name}' not found")

    if needs_approval(req.action_name, req.session_id):
        approval = request_approval(req.action_name, req.parameters)
        raise HTTPException(
            status_code=202,
            detail={"message": "Approval required", "approval_id": approval.id},
        )

    return await execute_action(req.action_name, req.parameters, dry_run=req.dry_run or settings.dry_run_mode)


@router.get("/approvals", response_model=list[PendingApproval])
async def list_approvals():
    return get_pending_approvals()


@router.post("/approve")
async def approve(decision: ApprovalDecision):
    found = resolve_approval(decision.approval_id, decision.approved)
    if not found:
        raise HTTPException(status_code=404, detail="Approval not found or already resolved")
    return {"status": "approved" if decision.approved else "denied"}
