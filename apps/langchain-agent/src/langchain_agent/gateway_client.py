from collections.abc import AsyncIterator
from typing import Any

import httpx

from langchain_agent.config import Settings


class GatewayClient:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def stream_chat_completion(
        self,
        *,
        message: str,
        model: str | None,
    ) -> AsyncIterator[str]:
        headers = self.auth_headers()
        async with (
            httpx.AsyncClient(timeout=None) as client,
            client.stream(
                "POST",
                self._settings.chat_completions_url,
                headers=headers,
                json={
                    "model": model or self._settings.default_model,
                    "stream": True,
                    "messages": [
                        {
                            "role": "user",
                            "content": message,
                        }
                    ],
                },
            ) as response,
        ):
            response.raise_for_status()
            async for chunk in response.aiter_text():
                if chunk:
                    yield chunk

    async def chat_completion(
        self,
        *,
        message: str,
        model: str | None,
    ) -> str:
        headers = self.auth_headers()
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                self._settings.chat_completions_url,
                headers=headers,
                json={
                    "model": model or self._settings.default_model,
                    "messages": [
                        {
                            "role": "user",
                            "content": message,
                        }
                    ],
                },
            )
            response.raise_for_status()

        payload: dict[str, Any] = response.json()
        choices = payload.get("choices", [])
        if not choices:
            return ""

        message_payload = choices[0].get("message", {})
        return str(message_payload.get("content") or "")

    def auth_headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._settings.production_gateway_api_key}",
            "Content-Type": "application/json",
        }
