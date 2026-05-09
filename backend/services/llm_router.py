from typing import Optional
from backend.config import settings
from backend.services.ollama_service import ollama_service
from backend.utils.logger import get_logger

logger = get_logger(__name__)

# Lazy imports for cloud providers to avoid errors when keys are not set
_openai_client = None
_anthropic_client = None


def _get_openai():
    global _openai_client
    if _openai_client is None and settings.openai_api_key:
        from openai import AsyncOpenAI
        _openai_client = AsyncOpenAI(api_key=settings.openai_api_key)
    return _openai_client


def _get_anthropic():
    global _anthropic_client
    if _anthropic_client is None and settings.anthropic_api_key:
        import anthropic
        _anthropic_client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
    return _anthropic_client


class LLMRouter:
    """Routes inference requests to the appropriate model provider."""

    async def get_available_models(self) -> list[dict]:
        models = []

        # Ollama models
        if await ollama_service.is_available():
            ollama_models = await ollama_service.list_models()
            for m in ollama_models:
                models.append({
                    "id": m["name"],
                    "name": m["name"],
                    "provider": "ollama",
                    "available": True,
                    "size": m.get("size"),
                })
        else:
            # Show default Gemma even if not yet pulled
            models.append({
                "id": settings.ollama_default_model,
                "name": settings.ollama_default_model,
                "provider": "ollama",
                "available": False,
                "description": "Not yet pulled. Run: ollama pull gemma3:4b",
            })

        # OpenAI models
        if settings.openai_api_key:
            for m in ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"]:
                models.append({"id": m, "name": m, "provider": "openai", "available": True})

        # Anthropic models
        if settings.anthropic_api_key:
            for m in ["claude-opus-4-7", "claude-sonnet-4-6", "claude-haiku-4-5-20251001"]:
                models.append({"id": m, "name": m, "provider": "anthropic", "available": True})

        return models

    def _pick_model(self, requested_model: Optional[str]) -> tuple[str, str]:
        """Return (model_id, provider)."""
        if requested_model:
            if requested_model.startswith("gpt-"):
                return requested_model, "openai"
            if requested_model.startswith("claude-"):
                return requested_model, "anthropic"
            return requested_model, "ollama"

        strategy = settings.model_routing
        if strategy == "local_only" or not (settings.openai_api_key or settings.anthropic_api_key):
            return settings.ollama_default_model, "ollama"
        if strategy == "cloud_first" and settings.openai_api_key:
            return "gpt-4o-mini", "openai"
        return settings.ollama_default_model, "ollama"

    async def chat(
        self,
        messages: list[dict],
        model: Optional[str] = None,
        images: Optional[list[str]] = None,
    ) -> tuple[str, str]:
        """Returns (response_text, model_used)."""
        model_id, provider = self._pick_model(model)

        try:
            if provider == "ollama":
                response = await ollama_service.chat(model_id, messages)
                return response, model_id

            if provider == "openai":
                client = _get_openai()
                if not client:
                    logger.warning("OpenAI key missing, falling back to Ollama")
                    response = await ollama_service.chat(settings.ollama_default_model, messages)
                    return response, settings.ollama_default_model

                oai_messages = []
                for m in messages:
                    content = m["content"]
                    if images and m["role"] == "user":
                        content_parts = [{"type": "text", "text": content}]
                        for img in images:
                            content_parts.append({
                                "type": "image_url",
                                "image_url": {"url": f"data:image/png;base64,{img}"},
                            })
                        oai_messages.append({"role": m["role"], "content": content_parts})
                    else:
                        oai_messages.append({"role": m["role"], "content": content})

                resp = await client.chat.completions.create(model=model_id, messages=oai_messages)
                return resp.choices[0].message.content, model_id

            if provider == "anthropic":
                client = _get_anthropic()
                if not client:
                    logger.warning("Anthropic key missing, falling back to Ollama")
                    response = await ollama_service.chat(settings.ollama_default_model, messages)
                    return response, settings.ollama_default_model

                system_msg = next((m["content"] for m in messages if m["role"] == "system"), "")
                user_messages = [m for m in messages if m["role"] != "system"]

                resp = await client.messages.create(
                    model=model_id,
                    max_tokens=4096,
                    system=system_msg or "You are a helpful macOS desktop agent.",
                    messages=user_messages,
                )
                return resp.content[0].text, model_id

        except Exception as e:
            logger.error(f"LLM error with {provider}/{model_id}: {e}")
            # Fallback to local
            if provider != "ollama":
                logger.info("Falling back to local Ollama model")
                response = await ollama_service.chat(settings.ollama_default_model, messages)
                return response, settings.ollama_default_model
            raise


llm_router = LLMRouter()
