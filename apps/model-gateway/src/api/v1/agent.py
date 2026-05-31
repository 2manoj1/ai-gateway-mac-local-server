from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, status
from fastapi.responses import StreamingResponse

from src.dependencies.auth import AuthContextDependency, extract_api_key
from src.dependencies.services import get_direct_message_agent_service
from src.schemas.agent import DirectMessageRequest
from src.services.agent_service import DirectMessageAgentService

router = APIRouter(
    prefix="/agent",
    tags=["Agent"],
)


@router.post(
    "/direct-message",
    summary="Stream a direct message through the LangGraph agent",
    description=(
        "Runs a LangGraph agent that calls the gateway's internal "
        "OpenAI-compatible LLM streaming service and returns Server-Sent Events."
    ),
    responses={
        200: {
            "description": "OpenAI-compatible chat completion chunks.",
            "content": {
                "text/event-stream": {
                    "example": (
                        'data: {"id":"chatcmpl-...","object":"chat.completion.chunk",'
                        '"choices":[{"index":0,"delta":{"content":"hello"}}]}'
                        "\n\ndata: [DONE]\n\n"
                    ),
                },
            },
        },
        401: {
            "description": "Missing or invalid API key.",
        },
    },
)
async def direct_message(
    request: DirectMessageRequest,
    auth_context: AuthContextDependency,
    agent_service: Annotated[
        DirectMessageAgentService,
        Depends(get_direct_message_agent_service),
    ],
) -> StreamingResponse:
    return StreamingResponse(
        agent_service.stream_direct_message(
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


@router.post(
    "/direct-message/completions-api",
    summary="Stream a direct message through the HTTP completions API",
    description=(
        "Runs a LangGraph agent that calls this gateway's "
        "`/v1/chat/completions` endpoint over HTTP. This is useful for testing "
        "the exact API boundary other microservices should call."
    ),
    responses={
        200: {
            "description": "OpenAI-compatible chat completion chunks.",
            "content": {
                "text/event-stream": {
                    "example": (
                        'data: {"id":"chatcmpl-...","object":"chat.completion.chunk",'
                        '"choices":[{"index":0,"delta":{"content":"hello"}}]}'
                        "\n\ndata: [DONE]\n\n"
                    ),
                },
            },
        },
        401: {
            "description": "Missing or invalid API key.",
        },
    },
)
async def direct_message_via_completions_api(
    request: DirectMessageRequest,
    auth_context: AuthContextDependency,
    agent_service: Annotated[
        DirectMessageAgentService,
        Depends(get_direct_message_agent_service),
    ],
    x_api_key: Annotated[str | None, Header(alias="X-API-Key")] = None,
    authorization: Annotated[str | None, Header(alias="Authorization")] = None,
) -> StreamingResponse:
    _ = auth_context
    api_key = extract_api_key(
        x_api_key=x_api_key,
        authorization=authorization,
    )

    if api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )

    return StreamingResponse(
        agent_service.stream_direct_message_via_completion_api(
            request=request,
            api_key=api_key,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
