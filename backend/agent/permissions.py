"""Permission manager — tracks per-action approval state."""
import uuid
from datetime import datetime
from backend.models.action import RiskLevel, PendingApproval
from backend.automation.actions import ACTION_REGISTRY
from backend.config import settings
from backend.utils.logger import get_logger

logger = get_logger(__name__)

# In-memory store of pending approvals (keyed by approval_id)
_pending: dict[str, PendingApproval] = {}

# Per-session granted permissions (persists for session lifetime)
_session_grants: dict[str, set[str]] = {}


def needs_approval(action_name: str, session_id: str) -> bool:
    """Return True if this action requires interactive approval right now."""
    if settings.safe_mode:
        definition = ACTION_REGISTRY.get(action_name)
        return definition is not None and definition.risk_level != RiskLevel.low

    if not settings.require_confirmation_for_actions:
        return False

    definition = ACTION_REGISTRY.get(action_name)
    if definition is None:
        return True  # unknown action — always confirm

    if definition.risk_level == RiskLevel.low:
        return False

    # Check session-level grants
    granted = _session_grants.get(session_id, set())
    if action_name in granted:
        return False

    return True


def request_approval(action_name: str, parameters: dict) -> PendingApproval:
    definition = ACTION_REGISTRY.get(action_name)
    approval_id = str(uuid.uuid4())
    approval = PendingApproval(
        id=approval_id,
        action_name=action_name,
        description=definition.description if definition else action_name,
        parameters=parameters,
        risk_level=definition.risk_level if definition else RiskLevel.high,
    )
    _pending[approval_id] = approval
    logger.info(f"Approval requested: {approval_id} for action {action_name}")
    return approval


def resolve_approval(approval_id: str, approved: bool, session_id: str = "default") -> bool:
    """Return True if approval was found and resolved."""
    approval = _pending.pop(approval_id, None)
    if approval is None:
        return False

    if approved:
        # Grant permission for this action in this session
        _session_grants.setdefault(session_id, set()).add(approval.action_name)
        logger.info(f"Approved: {approval.action_name} by session {session_id}")
    else:
        logger.info(f"Denied: {approval.action_name}")
    return True


def get_pending_approvals(session_id: str | None = None) -> list[PendingApproval]:
    return list(_pending.values())


def clear_session_grants(session_id: str):
    _session_grants.pop(session_id, None)
