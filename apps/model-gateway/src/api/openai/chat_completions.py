from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse

from src.dependencies.auth import AuthContextDependency
from src.dependencies.services import get_openai_service
from src.schemas.openai import ChatCompletionRequest, ChatCompletionResponse
from src.services.openai_service import OpenAICompatibleService

router = APIRouter(tags=["OpenAI Compatible"])

STREAMING_EXAMPLE = "\n\n".join(
    [
        'data: {"id":"chatcmpl-...","object":"chat.completion.chunk",'
        '"created":1780200000,"model":"qwen3.5:9b",'
        '"choices":[{"index":0,"delta":{"role":"assistant"}}]}',
        'data: {"id":"chatcmpl-...","object":"chat.completion.chunk",'
        '"created":1780200000,"model":"qwen3.5:9b",'
        '"choices":[{"index":0,"delta":{"content":"hello"}}]}',
        'data: {"id":"chatcmpl-...","object":"chat.completion.chunk",'
        '"created":1780200000,"model":"qwen3.5:9b",'
        '"choices":[{"index":0,"delta":{},"finish_reason":"stop"}]}',
        "data: [DONE]",
    ]
)


@router.post(
    "/chat/completions",
    response_model=ChatCompletionResponse,
    summary="Create a chat completion",
    description=(
        "OpenAI-compatible chat completions endpoint backed by Ollama. "
        "Set `stream=true` in the request body or query string to receive "
        "Server-Sent Events using OpenAI-style `chat.completion.chunk` payloads."
    ),
    operation_id="createChatCompletion",
    responses={
        200: {
            "description": (
                "Chat completion response, or SSE stream when streaming is enabled."
            ),
            "content": {
                "application/json": {
                    "example": {
                        "id": "chatcmpl-0f5c7f0c6f2b4c01a54f495f7fcd929a",
                        "object": "chat.completion",
                        "created": 1780200000,
                        "model": "qwen3.5:9b",
                        "choices": [
                            {
                                "index": 0,
                                "message": {
                                    "role": "assistant",
                                    "content": "hello",
                                },
                                "finish_reason": "stop",
                            }
                        ],
                    }
                },
                "text/event-stream": {
                    "example": STREAMING_EXAMPLE,
                },
            },
        },
        401: {
            "description": "Missing or invalid API key.",
        },
        502: {
            "description": "Ollama is unavailable or returned an upstream error.",
        },
    },
)
async def chat_completions(
    request: ChatCompletionRequest,
    auth_context: AuthContextDependency,
    openai_service: Annotated[OpenAICompatibleService, Depends(get_openai_service)],
    stream: Annotated[
        bool | None,
        Query(
            description=(
                "Enable Server-Sent Events streaming. Equivalent to setting "
                "`stream: true` in the JSON body."
            ),
        ),
    ] = None,
) -> ChatCompletionResponse | StreamingResponse:
    if stream or request.stream:
        return StreamingResponse(
            openai_service.stream_chat_completion(
                request=request,
                auth_context=auth_context,
            ),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    return await openai_service.create_chat_completion(
        request=request,
        auth_context=auth_context,
    )
