from typing import Annotated

from fastapi import APIRouter, Depends

from src.dependencies.auth import AuthContextDependency
from src.dependencies.services import get_openai_service
from src.schemas.openai import ChatCompletionRequest, ChatCompletionResponse
from src.services.openai_service import OpenAICompatibleService

router = APIRouter(tags=["OpenAI Compatible"])


@router.post("/chat/completions", response_model=ChatCompletionResponse)
async def chat_completions(
    request: ChatCompletionRequest,
    auth_context: AuthContextDependency,
    openai_service: Annotated[OpenAICompatibleService, Depends(get_openai_service)],
) -> ChatCompletionResponse:
    return await openai_service.create_chat_completion(
        request=request,
        auth_context=auth_context,
    )
