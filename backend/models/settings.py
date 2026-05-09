from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime


class ProviderConfig(BaseModel):
    provider: Literal["ollama", "openai", "anthropic"]
    enabled: bool = True
    api_key: Optional[str] = None  # masked in responses
    base_url: Optional[str] = None


class ModelRoutingConfig(BaseModel):
    strategy: Literal["local_first", "cloud_first", "local_only"] = "local_first"
    default_local_model: str = "gemma3:4b"
    default_cloud_model: Optional[str] = None
    advanced_task_model: Optional[str] = None


class SafetyConfig(BaseModel):
    require_confirmation: bool = True
    dry_run_mode: bool = False
    safe_mode: bool = False
    high_risk_actions: list[str] = [
        "send_email", "delete_file", "move_file", "bulk_action", "browser_payment"
    ]


class PermissionConfig(BaseModel):
    screen_capture: bool = False
    accessibility: bool = False
    mail_access: bool = False
    finder_access: bool = True
    clipboard_access: bool = True
    app_control: dict[str, bool] = {}


class AppSettingsModel(BaseModel):
    providers: list[ProviderConfig] = []
    routing: ModelRoutingConfig = ModelRoutingConfig()
    safety: SafetyConfig = SafetyConfig()
    permissions: PermissionConfig = PermissionConfig()
    onboarding_complete: bool = False
    updated_at: datetime = datetime.utcnow()


class SetupRequest(BaseModel):
    ollama_model: str = "gemma3:4b"
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    routing_strategy: Literal["local_first", "cloud_first", "local_only"] = "local_first"
