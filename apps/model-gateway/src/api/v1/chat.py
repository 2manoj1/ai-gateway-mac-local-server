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
    choices = completion.get("choices", [])
    content = ""

    if choices:
        message = choices[0].get("message", {})
        value = message.get("content", "")
        content = value if isinstance(value, str) else str(value)

    return ChatResponse(response=content)
