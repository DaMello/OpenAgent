from __future__ import annotations

from typing import Any

import httpx

from ..config import Settings


class QwenOllamaProvider:
    def __init__(self, settings: Settings):
        self.settings = settings

    async def installed_models(self) -> list[str]:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(f"{self.settings.ollama_url}/api/tags")
            response.raise_for_status()
            payload = response.json()
        return [m.get("name", "") for m in payload.get("models", []) if m.get("name")]

    async def resolve_model(self) -> str:
        if self.settings.model:
            return self.settings.model
        models = await self.installed_models()
        qwen = [name for name in models if "qwen" in name.lower()]
        if not qwen:
            raise RuntimeError(
                "No Qwen model was found in Ollama. Install one or set OPENAGENT_MODEL."
            )
        return qwen[0]

    async def chat(
        self,
        messages: list[dict[str, str]],
        *,
        think: bool = True,
        num_predict: int = 4096,
        temperature: float = 0.2,
    ) -> str:
        model = await self.resolve_model()
        payload: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "stream": False,
            "think": think,
            "options": {
                "num_ctx": self.settings.context_window,
                "num_predict": num_predict,
                "temperature": temperature,
            },
        }
        async with httpx.AsyncClient(timeout=None) as client:
            response = await client.post(
                f"{self.settings.ollama_url}/api/chat",
                json=payload,
            )
            response.raise_for_status()
            data = response.json()

        message = data.get("message") or {}
        content = message.get("content")
        if not content:
            content = message.get("thinking") or ""
        return str(content)
