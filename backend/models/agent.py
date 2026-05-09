from pydantic import BaseModel, Field
from typing import Optional, Any, Literal
from datetime import datetime
from enum import Enum


class MessageRole(str, Enum):
    user = "user"
    assistant = "assistant"
    system = "system"
    tool = "tool"


class AttachmentType(str, Enum):
    image = "image"
    file = "file"
    screenshot = "screenshot"
    text = "text"


class Attachment(BaseModel):
    type: AttachmentType
    name: str
    content: str  # base64 for images, text content for files
    mime_type: str = "text/plain"


class ChatMessage(BaseModel):
    role: MessageRole
    content: str
    attachments: list[Attachment] = []
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"
    model: Optional[str] = None
    attachments: list[Attachment] = []
    allow_actions: bool = True


class ChatResponse(BaseModel):
    session_id: str
    message: str
    model_used: str
    actions_taken: list[dict] = []
    pending_approvals: list[dict] = []
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ModelInfo(BaseModel):
    id: str
    name: str
    provider: Literal["ollama", "openai", "anthropic"]
    available: bool = True
    size: Optional[str] = None
    description: str = ""


class AgentStatus(BaseModel):
    status: Literal["idle", "thinking", "acting", "waiting_approval", "error"]
    current_task: Optional[str] = None
    model: Optional[str] = None
    session_id: Optional[str] = None
