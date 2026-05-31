from typing import Annotated

from fastapi import APIRouter, Depends

from src.dependencies.auth import AuthContextDependency, verify_api_key
from src.dependencies.services import get_openai_service
from src.schemas.openai import ModelsResponse
from src.services.openai_service import OpenAICompatibleService

router = APIRouter(
    tags=["Models"],
    dependencies=[Depends(verify_api_key)],
)


@router.get("/models", response_model=ModelsResponse)
async def models(
    auth_context: AuthContextDependency,
    openai_service: Annotated[
        OpenAICompatibleService,
        Depends(get_openai_service),
    ],
) -> ModelsResponse:
    return await openai_service.list_models(
        auth_context=auth_context,
    )
