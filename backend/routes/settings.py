from fastapi import APIRouter, HTTPException
from sqlalchemy import select, update
from backend.database import AsyncSessionLocal, AppSettings
from backend.models.settings import AppSettingsModel, SetupRequest
from backend.services.keychain_service import save_api_key, get_api_key, mask_key
from backend.config import settings
import json
from datetime import datetime

router = APIRouter(prefix="/settings", tags=["settings"])

SETTINGS_KEY = "app_settings"


async def _load_settings() -> dict:
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(AppSettings).where(AppSettings.key == SETTINGS_KEY))
        row = result.scalar_one_or_none()
        if row:
            return json.loads(row.value)
        return {}


async def _save_settings(data: dict):
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(AppSettings).where(AppSettings.key == SETTINGS_KEY))
        row = result.scalar_one_or_none()
        serialized = json.dumps(data, default=str)
        if row:
            row.value = serialized
            row.updated_at = datetime.utcnow()
        else:
            db.add(AppSettings(key=SETTINGS_KEY, value=serialized))
        await db.commit()


@router.get("/")
async def get_settings():
    data = await _load_settings()
    # Mask API keys before returning
    for provider in data.get("providers", []):
        if provider.get("api_key"):
            provider["api_key"] = mask_key(provider["api_key"])
    return data


@router.post("/setup")
async def complete_setup(req: SetupRequest):
    """First-run setup endpoint."""
    current = await _load_settings()

    providers = []
    providers.append({"provider": "ollama", "enabled": True, "base_url": settings.ollama_base_url})

    if req.openai_api_key:
        save_api_key("openai", req.openai_api_key)
        providers.append({"provider": "openai", "enabled": True})
        settings.openai_api_key = req.openai_api_key

    if req.anthropic_api_key:
        save_api_key("anthropic", req.anthropic_api_key)
        providers.append({"provider": "anthropic", "enabled": True})
        settings.anthropic_api_key = req.anthropic_api_key

    new_settings = {
        **current,
        "onboarding_complete": True,
        "providers": providers,
        "routing": {
            "strategy": req.routing_strategy,
            "default_local_model": req.ollama_model,
        },
        "safety": {
            "require_confirmation": settings.require_confirmation_for_actions,
            "dry_run_mode": settings.dry_run_mode,
            "safe_mode": settings.safe_mode,
        },
        "updated_at": datetime.utcnow().isoformat(),
    }

    settings.ollama_default_model = req.ollama_model
    settings.model_routing = req.routing_strategy

    await _save_settings(new_settings)
    return {"status": "ok", "message": "Setup complete"}


@router.get("/onboarding-status")
async def onboarding_status():
    data = await _load_settings()
    return {"complete": data.get("onboarding_complete", False)}


@router.put("/safety")
async def update_safety(require_confirmation: bool, dry_run: bool, safe_mode: bool):
    current = await _load_settings()
    current["safety"] = {
        "require_confirmation": require_confirmation,
        "dry_run_mode": dry_run,
        "safe_mode": safe_mode,
    }
    settings.require_confirmation_for_actions = require_confirmation
    settings.dry_run_mode = dry_run
    settings.safe_mode = safe_mode
    await _save_settings(current)
    return {"status": "ok"}
