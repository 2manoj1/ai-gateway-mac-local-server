from collections.abc import AsyncIterator
from typing import Any, cast

from src.clients.ollama import OllamaClient
from src.core.config import Settings
from src.dependencies.auth import AuthContext
from src.schemas.openai import (
    ChatCompletionRequest,
    CompletionRequest,
    EmbeddingRequest,
    ImageGenerationRequest,
    JsonDict,
    ModelObject,
    ModelsResponse,
    ResponseRequest,
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

    async def retrieve_model(
        self,
        *,
        model: str,
        auth_context: AuthContext,
    ) -> JsonDict:
        response = await self._ollama_client.retrieve_model(model)

        await self._usage_service.log_completion(
            api_key_id=auth_context.api_key_id,
            endpoint="/v1/models/{model}",
            model=model,
        )

        return self._dump_openai_object(response)

    async def create_chat_completion(
        self,
        *,
        request: ChatCompletionRequest,
        auth_context: AuthContext,
    ) -> JsonDict:
        payload = self._chat_payload(request)
        model = str(payload["model"])
        response = await self._ollama_client.chat_completion(payload=payload)

        await self._usage_service.log_completion(
            api_key_id=auth_context.api_key_id,
            endpoint="/v1/chat/completions",
            model=model,
        )

        return self._dump_openai_object(response)

    async def stream_chat_completion(
        self,
        *,
        request: ChatCompletionRequest,
        auth_context: AuthContext,
    ) -> AsyncIterator[str]:
        payload = self._chat_payload(request)
        model = str(payload["model"])

        async for chunk in self._ollama_client.stream_chat_completion(payload=payload):
            yield self._format_sse_data(chunk)
        yield "data: [DONE]\n\n"

        await self._usage_service.log_completion(
            api_key_id=auth_context.api_key_id,
            endpoint="/v1/chat/completions",
            model=model,
        )

    @staticmethod
    def _format_sse_data(data: str) -> str:
        return f"data: {data}\n\n"

    async def create_completion(
        self,
        *,
        request: CompletionRequest,
        auth_context: AuthContext,
    ) -> JsonDict:
        payload = self._request_payload(request)
        payload["model"] = payload.get("model") or self._settings.default_model
        model = str(payload["model"])
        response = await self._ollama_client.completion(payload=payload)

        await self._usage_service.log_completion(
            api_key_id=auth_context.api_key_id,
            endpoint="/v1/completions",
            model=model,
        )

        return self._dump_openai_object(response)

    async def stream_completion(
        self,
        *,
        request: CompletionRequest,
        auth_context: AuthContext,
    ) -> AsyncIterator[str]:
        payload = self._request_payload(request)
        payload["model"] = payload.get("model") or self._settings.default_model
        model = str(payload["model"])

        async for chunk in self._ollama_client.stream_completion(payload=payload):
            yield self._format_sse_data(chunk)
        yield "data: [DONE]\n\n"

        await self._usage_service.log_completion(
            api_key_id=auth_context.api_key_id,
            endpoint="/v1/completions",
            model=model,
        )

    async def create_embedding(
        self,
        *,
        request: EmbeddingRequest,
        auth_context: AuthContext,
    ) -> JsonDict:
        payload = self._request_payload(request)
        payload["model"] = payload.get("model") or self._settings.default_model
        model = str(payload["model"])
        response = await self._ollama_client.embedding(payload=payload)

        await self._usage_service.log_completion(
            api_key_id=auth_context.api_key_id,
            endpoint="/v1/embeddings",
            model=model,
        )

        return self._dump_openai_object(response)

    async def create_response(
        self,
        *,
        request: ResponseRequest,
        auth_context: AuthContext,
    ) -> JsonDict:
        payload = self._request_payload(request)
        payload["model"] = payload.get("model") or self._settings.default_model
        model = str(payload["model"])
        response = await self._ollama_client.response(payload=payload)

        await self._usage_service.log_completion(
            api_key_id=auth_context.api_key_id,
            endpoint="/v1/responses",
            model=model,
        )

        return self._dump_openai_object(response)

    async def stream_response(
        self,
        *,
        request: ResponseRequest,
        auth_context: AuthContext,
    ) -> AsyncIterator[str]:
        payload = self._request_payload(request)
        payload["model"] = payload.get("model") or self._settings.default_model
        model = str(payload["model"])

        async for event in self._ollama_client.stream_response(payload=payload):
            yield self._format_response_event(event)
        yield "event: done\ndata: [DONE]\n\n"

        await self._usage_service.log_completion(
            api_key_id=auth_context.api_key_id,
            endpoint="/v1/responses",
            model=model,
        )

    async def create_image_generation(
        self,
        *,
        request: ImageGenerationRequest,
        auth_context: AuthContext,
    ) -> JsonDict:
        payload = self._request_payload(request)
        model = str(payload.get("model") or "images")
        response = await self._ollama_client.image_generation(payload=payload)

        await self._usage_service.log_completion(
            api_key_id=auth_context.api_key_id,
            endpoint="/v1/images/generations",
            model=model,
        )

        return self._dump_openai_object(response)

    async def stream_image_generation(
        self,
        *,
        request: ImageGenerationRequest,
        auth_context: AuthContext,
    ) -> AsyncIterator[str]:
        payload = self._request_payload(request)
        model = str(payload.get("model") or "images")

        async for event in self._ollama_client.stream_image_generation(payload=payload):
            yield self._format_response_event(event)
        yield "event: done\ndata: [DONE]\n\n"

        await self._usage_service.log_completion(
            api_key_id=auth_context.api_key_id,
            endpoint="/v1/images/generations",
            model=model,
        )

    def _chat_payload(self, request: ChatCompletionRequest) -> JsonDict:
        payload = self._request_payload(request)
        payload["model"] = payload.get("model") or self._settings.default_model
        payload["keep_alive"] = self._normalize_keep_alive(
            payload.get("keep_alive") or self._settings.ollama_keep_alive,
        )

        if not payload.get("messages") and "prompt" in payload:
            payload["messages"] = [{"role": "user", "content": payload.pop("prompt")}]
        else:
            payload.pop("prompt", None)

        return payload

    @staticmethod
    def _request_payload(request: Any) -> JsonDict:
        return cast(JsonDict, request.model_dump(mode="json", exclude_unset=True))

    @staticmethod
    def _normalize_keep_alive(value: Any) -> Any:
        if isinstance(value, str):
            stripped = value.strip()
            if stripped.removeprefix("-").isdigit():
                return int(stripped)
        return value

    @staticmethod
    def _dump_openai_object(value: Any) -> JsonDict:
        if hasattr(value, "model_dump"):
            dumped = value.model_dump(mode="json", exclude_none=True)
            return dumped if isinstance(dumped, dict) else {"data": dumped}
        if isinstance(value, dict):
            return value
        return {"data": value}

    @staticmethod
    def _format_response_event(data: str) -> str:
        event_type = OpenAICompatibleService._event_type_from_json(data)
        if event_type is None:
            return OpenAICompatibleService._format_sse_data(data)
        return f"event: {event_type}\ndata: {data}\n\n"

    @staticmethod
    def _event_type_from_json(data: str) -> str | None:
        marker = '"type":"'
        start = data.find(marker)
        if start == -1:
            return None

        start += len(marker)
        end = data.find('"', start)
        if end == -1:
            return None

        return data[start:end]
