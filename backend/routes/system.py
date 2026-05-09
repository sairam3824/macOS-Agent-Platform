from fastapi import APIRouter
from backend.services.ollama_service import ollama_service
from backend.config import settings
import platform
import subprocess

router = APIRouter(prefix="/system", tags=["system"])


@router.get("/health")
async def health():
    ollama_ok = await ollama_service.is_available()
    return {
        "status": "ok",
        "platform": platform.system(),
        "ollama": "connected" if ollama_ok else "disconnected",
        "model_routing": settings.model_routing,
        "default_model": settings.ollama_default_model,
    }


@router.get("/info")
async def system_info():
    """System capabilities and permissions status."""
    result = {
        "os": platform.mac_ver()[0],
        "python": platform.python_version(),
        "ollama_url": settings.ollama_base_url,
        "has_openai": bool(settings.openai_api_key),
        "has_anthropic": bool(settings.anthropic_api_key),
        "safe_mode": settings.safe_mode,
        "dry_run": settings.dry_run_mode,
    }
    return result


@router.post("/ollama/pull")
async def pull_model(model_name: str):
    """Trigger a model pull from Ollama registry."""
    # Returns immediately; streaming logs are not proxied here
    # Use the /api/pull Ollama endpoint directly for progress
    try:
        subprocess.Popen(
            ["ollama", "pull", model_name],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return {"status": "started", "model": model_name}
    except FileNotFoundError:
        return {"status": "error", "message": "ollama CLI not found"}


@router.get("/ollama/models")
async def ollama_models():
    models = await ollama_service.list_models()
    return models
