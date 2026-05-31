from collections.abc import Sequence
from typing import Any

import httpx
from langchain_core.callbacks.manager import (
    AsyncCallbackManagerForLLMRun,
    CallbackManagerForLLMRun,
)
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.outputs import ChatGeneration, ChatResult

from langchain_agent.config import Settings
from langchain_agent.gateway_client import GatewayClient


class GatewayChatModel(BaseChatModel):
    settings: Settings
    model_name: str

    @property
    def _llm_type(self) -> str:
        return "ai-gateway-httpx-chat"

    async def _agenerate(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager: AsyncCallbackManagerForLLMRun | None = None,
        **kwargs: Any,
    ) -> ChatResult:
        _ = (stop, run_manager, kwargs)
        content = await self._acompletion(messages)
        return ChatResult(
            generations=[
                ChatGeneration(
                    message=AIMessage(content=content),
                )
            ]
        )

    def _generate(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager: CallbackManagerForLLMRun | None = None,
        **kwargs: Any,
    ) -> ChatResult:
        _ = (stop, run_manager, kwargs)
        content = self._completion(messages)
        return ChatResult(
            generations=[
                ChatGeneration(
                    message=AIMessage(content=content),
                )
            ]
        )

    async def _acompletion(self, messages: Sequence[BaseMessage]) -> str:
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                self.settings.chat_completions_url,
                headers=GatewayClient(self.settings).auth_headers(),
                json={
                    "model": self.model_name,
                    "messages": self._serialize_messages(messages),
                },
            )
            response.raise_for_status()

        return self._extract_content(response.json())

    def _completion(self, messages: Sequence[BaseMessage]) -> str:
        with httpx.Client(timeout=120) as client:
            response = client.post(
                self.settings.chat_completions_url,
                headers=GatewayClient(self.settings).auth_headers(),
                json={
                    "model": self.model_name,
                    "messages": self._serialize_messages(messages),
                },
            )
            response.raise_for_status()

        return self._extract_content(response.json())

    @staticmethod
    def _serialize_messages(
        messages: Sequence[BaseMessage],
    ) -> list[dict[str, str]]:
        serialized: list[dict[str, str]] = []
        for message in messages:
            role = {
                "human": "user",
                "ai": "assistant",
                "system": "system",
            }.get(message.type, "user")
            serialized.append(
                {
                    "role": role,
                    "content": str(message.content),
                }
            )
        return serialized

    @staticmethod
    def _extract_content(payload: dict[str, Any]) -> str:
        choices = payload.get("choices", [])
        if not choices:
            return ""

        message_payload = choices[0].get("message", {})
        return str(message_payload.get("content") or "")
