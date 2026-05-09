from pydantic import BaseModel, Field
from typing import Optional, Any, Literal
from datetime import datetime
from enum import Enum


class ActionCategory(str, Enum):
    system = "system"
    file = "file"
    mail = "mail"
    browser = "browser"
    finder = "finder"
    clipboard = "clipboard"
    screenshot = "screenshot"
    app_control = "app_control"


class RiskLevel(str, Enum):
    low = "low"       # read-only, no side effects
    medium = "medium" # minor changes, reversible
    high = "high"     # destructive, irreversible, sends data


class ActionDefinition(BaseModel):
    name: str
    description: str
    category: ActionCategory
    risk_level: RiskLevel
    parameters_schema: dict = {}
    requires_permission: bool = False


class ActionRequest(BaseModel):
    action_name: str
    parameters: dict = {}
    session_id: str = "default"
    dry_run: bool = False


class ActionResult(BaseModel):
    action_name: str
    success: bool
    output: Any = None
    error: Optional[str] = None
    dry_run: bool = False
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class PendingApproval(BaseModel):
    id: str
    action_name: str
    description: str
    parameters: dict
    risk_level: RiskLevel
    requested_at: datetime = Field(default_factory=datetime.utcnow)


class ApprovalDecision(BaseModel):
    approval_id: str
    approved: bool
    reason: Optional[str] = None
