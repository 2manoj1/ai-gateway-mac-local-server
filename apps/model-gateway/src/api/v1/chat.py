from typing import Annotated

from fastapi import APIRouter, Depends

from src.dependencies.auth import AuthContextDependency
from src.dependencies.services import get_openai_service
from src.schemas.chat import ChatRequest, ChatResponse
from src.schemas.openai import ChatCompletionRequest, ChatMessage
from src.services.openai_service import OpenAICompatibleService

router = APIRouter(
    tags=["Chat"],
)


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    auth_context: AuthContextDependency,
    openai_service: Annotated[OpenAICompatibleService, Depends(get_openai_service)],
) -> ChatResponse:
    completion = await openai_service.create_chat_completion(
        request=ChatCompletionRequest(
            messages=[
                ChatMessage(
                    role="user",
                    content=request.prompt,
                )
            ],
        ),
        auth_context=auth_context,
    )
    return ChatResponse(response=completion.choices[0].message.content)
