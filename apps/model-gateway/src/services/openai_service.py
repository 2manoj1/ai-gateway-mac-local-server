from collections.abc import AsyncIterator
from time import time
from uuid import uuid4

from src.clients.ollama import OllamaClient
from src.core.config import Settings
from src.dependencies.auth import AuthContext
from src.schemas.openai import (
    ChatCompletionChoice,
    ChatCompletionChunk,
    ChatCompletionChunkChoice,
    ChatCompletionChunkDelta,
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

    async def list_models(
        self,
        *,
        auth_context: AuthContext,
    ) -> ModelsResponse:
        models = await self._ollama_client.list_models()
        response = ModelsResponse(
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
        await self._usage_service.log_completion(
            api_key_id=auth_context.api_key_id,
            endpoint="/v1/models",
            model="models",
        )
        return response

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

    async def stream_chat_completion(
        self,
        *,
        request: ChatCompletionRequest,
        auth_context: AuthContext,
    ) -> AsyncIterator[str]:
        model = request.model or self._settings.default_model
        completion_id = f"chatcmpl-{uuid4().hex}"
        created = int(time())

        yield self._format_sse_data(
            ChatCompletionChunk(
                id=completion_id,
                created=created,
                model=model,
                choices=[
                    ChatCompletionChunkChoice(
                        index=0,
                        delta=ChatCompletionChunkDelta(role="assistant"),
                    )
                ],
            ).model_dump_json(exclude_none=True)
        )

        async for content in self._ollama_client.stream_chat_completion(
            model=model,
            messages=request.messages,
        ):
            yield self._format_sse_data(
                ChatCompletionChunk(
                    id=completion_id,
                    created=created,
                    model=model,
                    choices=[
                        ChatCompletionChunkChoice(
                            index=0,
                            delta=ChatCompletionChunkDelta(content=content),
                        )
                    ],
                ).model_dump_json(exclude_none=True)
            )

        yield self._format_sse_data(
            ChatCompletionChunk(
                id=completion_id,
                created=created,
                model=model,
                choices=[
                    ChatCompletionChunkChoice(
                        index=0,
                        delta=ChatCompletionChunkDelta(),
                        finish_reason="stop",
                    )
                ],
            ).model_dump_json(exclude_none=True)
        )
        yield "data: [DONE]\n\n"

        await self._usage_service.log_completion(
            api_key_id=auth_context.api_key_id,
            endpoint="/v1/chat/completions",
            model=model,
        )

    @staticmethod
    def _format_sse_data(data: str) -> str:
        return f"data: {data}\n\n"
