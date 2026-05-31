from typing import Annotated

from fastapi import APIRouter, Depends

from src.dependencies.auth import verify_api_key
from src.dependencies.services import get_openai_service
from src.schemas.openai import ModelsResponse
from src.services.openai_service import OpenAICompatibleService

router = APIRouter(
    tags=["Models"],
    dependencies=[Depends(verify_api_key)],
)


@router.get("/models", response_model=ModelsResponse)
async def models(
    openai_service: Annotated[OpenAICompatibleService, Depends(get_openai_service)],
) -> ModelsResponse:
    return await openai_service.list_models()
