from typing import Annotated

from fastapi import APIRouter, Depends

from src.dependencies.auth import AuthContextDependency
from src.dependencies.services import get_openai_service
from src.schemas.openai import EmbeddingRequest, JsonDict
from src.services.openai_service import OpenAICompatibleService

router = APIRouter(tags=["OpenAI Compatible"])


@router.post(
    "/embeddings",
    response_model=None,
    summary="Create embeddings",
    description=(
        "OpenAI-compatible embeddings endpoint backed by Ollama. "
        "Provider-specific request fields are passed through when possible."
    ),
    operation_id="createEmbedding",
    responses={
        200: {
            "description": "OpenAI-compatible embedding response.",
        },
        401: {
            "description": "Missing or invalid API key.",
        },
        502: {
            "description": "Ollama is unavailable or returned an upstream error.",
        },
    },
)
async def embeddings(
    request: EmbeddingRequest,
    auth_context: AuthContextDependency,
    openai_service: Annotated[OpenAICompatibleService, Depends(get_openai_service)],
) -> JsonDict:
    return await openai_service.create_embedding(
        request=request,
        auth_context=auth_context,
    )
