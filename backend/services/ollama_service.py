import httpx
from typing import AsyncIterator, Optional
from backend.config import settings
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class OllamaService:
    def __init__(self):
        self.base_url = settings.ollama_base_url
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=120.0)

    async def is_available(self) -> bool:
        try:
            resp = await self.client.get("/api/tags")
            return resp.status_code == 200
        except Exception:
            return False

    async def list_models(self) -> list[dict]:
        try:
            resp = await self.client.get("/api/tags")
            resp.raise_for_status()
            data = resp.json()
            return data.get("models", [])
        except Exception as e:
            logger.warning(f"Failed to list Ollama models: {e}")
            return []

    async def pull_model(self, model_name: str) -> AsyncIterator[str]:
        async with self.client.stream("POST", "/api/pull", json={"name": model_name}) as resp:
            async for line in resp.aiter_lines():
                if line:
                    yield line

    async def chat(
        self,
        model: str,
        messages: list[dict],
        images: Optional[list[str]] = None,
        stream: bool = False,
    ) -> str:
        payload: dict = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": 0.7},
        }

        if stream:
            collected = []
            async with self.client.stream("POST", "/api/chat", json={**payload, "stream": True}) as resp:
                import json
                async for line in resp.aiter_lines():
                    if line:
                        try:
                            chunk = json.loads(line)
                            if chunk.get("message", {}).get("content"):
                                collected.append(chunk["message"]["content"])
                        except Exception:
                            pass
            return "".join(collected)

        resp = await self.client.post("/api/chat", json=payload)
        resp.raise_for_status()
        data = resp.json()
        return data.get("message", {}).get("content", "")

    async def generate_with_image(self, model: str, prompt: str, image_b64: str) -> str:
        # Use vision-capable models or fallback to chat with image in message
        messages = [
            {
                "role": "user",
                "content": prompt,
                "images": [image_b64],
            }
        ]
        return await self.chat(model, messages)

    async def close(self):
        await self.client.aclose()


ollama_service = OllamaService()
