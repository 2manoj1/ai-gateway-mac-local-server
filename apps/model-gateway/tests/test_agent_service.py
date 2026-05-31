from collections.abc import AsyncIterator
from typing import cast

import httpx
import pytest
from pytest_httpx import HTTPXMock
from src.core.config import get_settings
from src.dependencies.auth import AuthContext
from src.schemas.agent import DirectMessageRequest
from src.schemas.openai import ChatCompletionRequest
from src.services.agent_service import DirectMessageAgentService
from src.services.openai_service import OpenAICompatibleService


class FakeOpenAIService:
    def __init__(self) -> None:
        self.request: ChatCompletionRequest | None = None
        self.auth_context: AuthContext | None = None

    async def stream_chat_completion(
        self,
        *,
        request: ChatCompletionRequest,
        auth_context: AuthContext,
    ) -> AsyncIterator[str]:
        self.request = request
        self.auth_context = auth_context
        yield 'data: {"choices":[{"delta":{"content":"hel"}}]}\n\n'
        yield 'data: {"choices":[{"delta":{"content":"lo"}}]}\n\n'
        yield "data: [DONE]\n\n"


@pytest.mark.asyncio
async def test_direct_message_agent_streams_internal_llm_chunks() -> None:
    openai_service = FakeOpenAIService()
    service = DirectMessageAgentService(
        settings=get_settings(),
        openai_service=cast(OpenAICompatibleService, openai_service),
    )
    auth_context = AuthContext(api_key_id=None, api_key_name="test")

    chunks = [
        chunk
        async for chunk in service.stream_direct_message(
            request=DirectMessageRequest(
                message="hello",
                model="qwen3.5:9b",
            ),
            auth_context=auth_context,
        )
    ]

    assert chunks == [
        'data: {"choices":[{"delta":{"content":"hel"}}]}\n\n',
        'data: {"choices":[{"delta":{"content":"lo"}}]}\n\n',
        "data: [DONE]\n\n",
    ]
    assert openai_service.request is not None
    assert openai_service.request.model == "qwen3.5:9b"
    assert openai_service.request.stream is True
    assert openai_service.request.messages[0].content == "hello"
    assert openai_service.auth_context == auth_context


@pytest.mark.asyncio
async def test_direct_message_agent_can_stream_via_completion_api(
    httpx_mock: HTTPXMock,
) -> None:
    settings = get_settings()
    httpx_mock.add_response(
        method="POST",
        url=f"{settings.internal_gateway_base_url}/v1/chat/completions",
        stream=httpx.ByteStream(
            b'data: {"choices":[{"delta":{"content":"agent"}}]}\n\ndata: [DONE]\n\n'
        ),
    )
    service = DirectMessageAgentService(
        settings=settings,
        openai_service=cast(OpenAICompatibleService, FakeOpenAIService()),
    )

    chunks = [
        chunk
        async for chunk in service.stream_direct_message_via_completion_api(
            request=DirectMessageRequest(
                message="hello",
                model="qwen3.5:9b",
            ),
            api_key="sk_test",
        )
    ]
    outbound_request = httpx_mock.get_request()

    assert outbound_request is not None
    assert outbound_request.headers["Authorization"] == "Bearer sk_test"
    assert b'"stream":true' in outbound_request.read()
    assert chunks == [
        'data: {"choices":[{"delta":{"content":"agent"}}]}\n\ndata: [DONE]\n\n'
    ]
