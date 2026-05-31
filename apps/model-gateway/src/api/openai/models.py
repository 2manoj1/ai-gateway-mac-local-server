from typing import Annotated

from fastapi import APIRouter, Depends

from src.dependencies.auth import AuthContextDependency
from src.dependencies.services import get_openai_service
from src.schemas.openai import ModelsResponse
from src.services.openai_service import OpenAICompatibleService

router = APIRouter(tags=["OpenAI Compatible"])


@router.get(
    "/models",
    response_model=ModelsResponse,
    summary="List available models",
    description=(
        "Returns models available through the configured Ollama backend in an "
        "OpenAI-compatible list response."
    ),
    operation_id="listModels",
    responses={
        200: {
            "description": "OpenAI-compatible model list.",
        },
        401: {
            "description": "Missing or invalid API key.",
        },
        502: {
            "description": "Ollama is unavailable or returned an upstream error.",
        },
    },
)
async def models(
    auth_context: AuthContextDependency,
    openai_service: Annotated[OpenAICompatibleService, Depends(get_openai_service)],
) -> ModelsResponse:
    return await openai_service.list_models(auth_context=auth_context)
