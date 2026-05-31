from typing import Any, cast

from openai import APIConnectionError, APIError, APITimeoutError, AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam

from src.core.config import Settings
from src.schemas.openai import ChatMessage


class OllamaClientError(RuntimeError):
    """Raised when Ollama cannot complete a client operation."""


class OllamaClient:
    def __init__(self, settings: Settings) -> None:
        self._client = AsyncOpenAI(
            api_key="ollama",
            base_url=settings.ollama_base_url,
        )

    async def close(self) -> None:
        await self._client.close()

    async def list_models(self) -> list[Any]:
        try:
            response = await self._client.models.list()
        except (APIConnectionError, APITimeoutError, APIError) as exc:
            raise OllamaClientError("Unable to fetch models from Ollama") from exc

        return list(response.data)

    async def chat_completion(
        self,
        *,
        model: str,
        messages: list[ChatMessage],
    ) -> str:
        openai_messages = cast(
            list[ChatCompletionMessageParam],
            [
                {
                    "role": message.role,
                    "content": message.content,
                }
                for message in messages
            ],
        )

        try:
            response = await self._client.chat.completions.create(
                model=model,
                messages=openai_messages,
            )
        except (APIConnectionError, APITimeoutError, APIError) as exc:
            raise OllamaClientError(
                "Unable to generate completion from Ollama"
            ) from exc

        if not response.choices:
            raise OllamaClientError("Ollama returned no chat choices")

        return response.choices[0].message.content or ""
