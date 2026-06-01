from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse

from src.dependencies.auth import AuthContextDependency
from src.dependencies.services import get_openai_service
from src.schemas.openai import ImageGenerationRequest, JsonDict
from src.services.openai_service import OpenAICompatibleService

router = APIRouter(tags=["OpenAI Compatible"])


@router.post(
    "/images/generations",
    response_model=None,
    summary="Generate an image",
    description=(
        "OpenAI-compatible image generation endpoint backed by Ollama image "
        "models where supported by the configured Ollama version."
    ),
    operation_id="createImageGeneration",
    responses={
        200: {
            "description": (
                "Image generation response, or SSE stream when streaming is enabled."
            ),
        },
        401: {
            "description": "Missing or invalid API key.",
        },
        502: {
            "description": "Ollama is unavailable or returned an upstream error.",
        },
    },
)
async def image_generations(
    request: ImageGenerationRequest,
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
) -> JsonDict | StreamingResponse:
    if stream or request.stream:
        return StreamingResponse(
            openai_service.stream_image_generation(
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

    return await openai_service.create_image_generation(
        request=request,
        auth_context=auth_context,
    )
