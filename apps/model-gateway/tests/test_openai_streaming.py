from collections.abc import AsyncIterator
from typing import cast

import pytest
from src.clients.ollama import OllamaClient
from src.core.config import get_settings
from src.dependencies.auth import AuthContext
from src.schemas.openai import ChatCompletionRequest, ChatMessage
from src.services.openai_service import OpenAICompatibleService
from src.services.usage_service import UsageLoggingService


class FakeOllamaClient:
    async def stream_chat_completion(
        self,
        *,
        model: str,
        messages: list[ChatMessage],
    ) -> AsyncIterator[str]:
        _ = (model, messages)
        yield "hel"
        yield "lo"


class FakeUsageLoggingService:
    def __init__(self) -> None:
        self.logged_model: str | None = None
        self.logged_endpoint: str | None = None

    async def log_completion(
        self,
        *,
        api_key_id: object,
        endpoint: str,
        model: str,
        tokens_input: int = 0,
        tokens_output: int = 0,
    ) -> None:
        _ = (api_key_id, tokens_input, tokens_output)
        self.logged_endpoint = endpoint
        self.logged_model = model


@pytest.mark.asyncio
async def test_stream_chat_completion_emits_openai_sse_chunks() -> None:
    usage_service = FakeUsageLoggingService()
    service = OpenAICompatibleService(
        settings=get_settings(),
        ollama_client=cast(OllamaClient, FakeOllamaClient()),
        usage_service=cast(UsageLoggingService, usage_service),
    )

    chunks = [
        chunk
        async for chunk in service.stream_chat_completion(
            request=ChatCompletionRequest(
                model="qwen3.5:9b",
                messages=[
                    ChatMessage(
                        role="user",
                        content="hello",
                    )
                ],
            ),
            auth_context=AuthContext(api_key_id=None, api_key_name="test"),
        )
    ]

    assert chunks[0].startswith("data: ")
    assert '"object":"chat.completion.chunk"' in chunks[0]
    assert '"role":"assistant"' in chunks[0]
    assert '"content":"hel"' in chunks[1]
    assert '"content":"lo"' in chunks[2]
    assert '"finish_reason":"stop"' in chunks[3]
    assert chunks[-1] == "data: [DONE]\n\n"
    assert usage_service.logged_endpoint == "/v1/chat/completions"
    assert usage_service.logged_model == "qwen3.5:9b"
