from time import time
from uuid import uuid4

from src.clients.ollama import OllamaClient
from src.core.config import Settings
from src.dependencies.auth import AuthContext
from src.schemas.openai import (
    ChatCompletionChoice,
    ChatCompletionMessage,
    ChatCompletionRequest,
    ChatCompletionResponse,
    ModelObject,
    ModelsResponse,
)
from src.services.usage_service import UsageLoggingService


class OpenAICompatibleService:
    def __init__(
        self,
        *,
        settings: Settings,
        ollama_client: OllamaClient,
        usage_service: UsageLoggingService,
    ) -> None:
        self._settings = settings
        self._ollama_client = ollama_client
        self._usage_service = usage_service

    async def list_models(self) -> ModelsResponse:
        models = await self._ollama_client.list_models()
        return ModelsResponse(
            data=[
                ModelObject(
                    id=model.id,
                    object="model",
                    created=getattr(model, "created", None),
                    owned_by=getattr(model, "owned_by", "ollama") or "ollama",
                )
                for model in models
            ],
        )

    async def create_chat_completion(
        self,
        *,
        request: ChatCompletionRequest,
        auth_context: AuthContext,
    ) -> ChatCompletionResponse:
        model = request.model or self._settings.default_model
        content = await self._ollama_client.chat_completion(
            model=model,
            messages=request.messages,
        )

        await self._usage_service.log_completion(
            api_key_id=auth_context.api_key_id,
            endpoint="/v1/chat/completions",
            model=model,
        )

        return ChatCompletionResponse(
            id=f"chatcmpl-{uuid4().hex}",
            created=int(time()),
            model=model,
            choices=[
                ChatCompletionChoice(
                    index=0,
                    message=ChatCompletionMessage(content=content),
                    finish_reason="stop",
                )
            ],
        )
