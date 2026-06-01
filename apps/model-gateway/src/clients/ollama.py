from collections.abc import AsyncIterator
from inspect import signature
from typing import Any, NoReturn, cast

from openai import (
    APIConnectionError,
    APIError,
    APIStatusError,
    APITimeoutError,
    AsyncOpenAI,
)

from src.core.config import Settings
from src.schemas.openai import JsonDict


class OllamaClientError(RuntimeError):
    """Raised when Ollama cannot complete a client operation."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int = 502,
        error_type: str = "ollama_error",
        code: str = "bad_gateway",
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.error_type = error_type
        self.code = code


class OllamaClient:
    def __init__(self, settings: Settings) -> None:
        self._client = AsyncOpenAI(
            api_key="ollama",
            base_url=settings.ollama_base_url,
            max_retries=0,
        )

    async def warmup(self, model: str) -> None:
        await self._client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": "warmup",
                }
            ],
            extra_body={"keep_alive": "-1"},
        )

    async def close(self) -> None:
        await self._client.close()

    async def list_models(self) -> list[Any]:
        try:
            response = await self._client.models.list()
        except (APIConnectionError, APITimeoutError, APIError) as exc:
            self._raise_client_error("Unable to fetch models from Ollama", exc)

        return list(response.data)

    async def retrieve_model(self, model: str) -> Any:
        try:
            return await self._client.models.retrieve(model)
        except (APIConnectionError, APITimeoutError, APIError) as exc:
            self._raise_client_error("Unable to fetch model from Ollama", exc)

    async def chat_completion(
        self,
        *,
        payload: JsonDict,
    ) -> Any:
        try:
            create = cast(Any, self._client.chat.completions.create)
            response = await create(
                **self._prepare_kwargs(
                    payload,
                    accepted_params=self._accepted_params(create),
                ),
            )
        except (APIConnectionError, APITimeoutError, APIError) as exc:
            self._raise_client_error(
                "Unable to generate completion from Ollama",
                exc,
            )

        return response

    async def stream_chat_completion(
        self,
        *,
        payload: JsonDict,
    ) -> AsyncIterator[str]:
        try:
            create = cast(Any, self._client.chat.completions.create)
            stream = await create(
                **self._prepare_kwargs(
                    {**payload, "stream": True},
                    accepted_params=self._accepted_params(create),
                ),
            )
        except (APIConnectionError, APITimeoutError, APIError) as exc:
            self._raise_client_error("Unable to stream completion from Ollama", exc)

        async for chunk in stream:
            yield chunk.model_dump_json(exclude_none=True)

    async def completion(
        self,
        *,
        payload: JsonDict,
    ) -> Any:
        try:
            create = cast(Any, self._client.completions.create)
            return await create(
                **self._prepare_kwargs(
                    payload,
                    accepted_params=self._accepted_params(create),
                ),
            )
        except (APIConnectionError, APITimeoutError, APIError) as exc:
            self._raise_client_error(
                "Unable to generate completion from Ollama",
                exc,
            )

    async def stream_completion(
        self,
        *,
        payload: JsonDict,
    ) -> AsyncIterator[str]:
        try:
            create = cast(Any, self._client.completions.create)
            stream = await create(
                **self._prepare_kwargs(
                    {**payload, "stream": True},
                    accepted_params=self._accepted_params(create),
                ),
            )
        except (APIConnectionError, APITimeoutError, APIError) as exc:
            self._raise_client_error("Unable to stream completion from Ollama", exc)

        async for chunk in stream:
            yield chunk.model_dump_json(exclude_none=True)

    async def embedding(
        self,
        *,
        payload: JsonDict,
    ) -> Any:
        try:
            create = cast(Any, self._client.embeddings.create)
            return await create(
                **self._prepare_kwargs(
                    payload,
                    accepted_params=self._accepted_params(create),
                ),
            )
        except (APIConnectionError, APITimeoutError, APIError) as exc:
            self._raise_client_error("Unable to create embedding from Ollama", exc)

    async def response(
        self,
        *,
        payload: JsonDict,
    ) -> Any:
        try:
            create = cast(Any, self._client.responses.create)
            return await create(
                **self._prepare_kwargs(
                    payload,
                    accepted_params=self._accepted_params(create),
                ),
            )
        except (APIConnectionError, APITimeoutError, APIError) as exc:
            self._raise_client_error("Unable to create response from Ollama", exc)

    async def stream_response(
        self,
        *,
        payload: JsonDict,
    ) -> AsyncIterator[str]:
        try:
            create = cast(Any, self._client.responses.create)
            stream = await create(
                **self._prepare_kwargs(
                    {**payload, "stream": True},
                    accepted_params=self._accepted_params(create),
                ),
            )
        except (APIConnectionError, APITimeoutError, APIError) as exc:
            self._raise_client_error("Unable to stream response from Ollama", exc)

        async for event in stream:
            yield event.model_dump_json(exclude_none=True)

    async def image_generation(
        self,
        *,
        payload: JsonDict,
    ) -> Any:
        try:
            create = cast(Any, self._client.images.generate)
            return await create(
                **self._prepare_kwargs(
                    payload,
                    accepted_params=self._accepted_params(create),
                ),
            )
        except (APIConnectionError, APITimeoutError, APIError) as exc:
            self._raise_client_error("Unable to generate image from Ollama", exc)

    async def stream_image_generation(
        self,
        *,
        payload: JsonDict,
    ) -> AsyncIterator[str]:
        try:
            create = cast(Any, self._client.images.generate)
            stream = await create(
                **self._prepare_kwargs(
                    {**payload, "stream": True},
                    accepted_params=self._accepted_params(create),
                ),
            )
        except (APIConnectionError, APITimeoutError, APIError) as exc:
            self._raise_client_error(
                "Unable to stream image generation from Ollama",
                exc,
            )

        async for event in stream:
            yield event.model_dump_json(exclude_none=True)

    @staticmethod
    def _accepted_params(method: Any) -> set[str]:
        return {
            name
            for name in signature(method).parameters
            if name not in {"extra_body", "extra_headers", "extra_query", "timeout"}
        }

    @staticmethod
    def _prepare_kwargs(
        payload: JsonDict,
        *,
        accepted_params: set[str],
    ) -> JsonDict:
        kwargs: JsonDict = {}
        extra_body: JsonDict = {}

        for key, value in payload.items():
            if key in accepted_params:
                kwargs[key] = value
            else:
                extra_body[key] = value

        if extra_body:
            kwargs["extra_body"] = extra_body

        return kwargs

    @staticmethod
    def _raise_client_error(message: str, exc: APIError) -> NoReturn:
        if isinstance(exc, APIStatusError):
            upstream_message = OllamaClient._upstream_error_message(exc)
            raise OllamaClientError(
                f"{message}: {upstream_message}",
                status_code=exc.status_code,
                error_type="upstream_error",
                code=str(exc.status_code),
            ) from exc

        raise OllamaClientError(message) from exc

    @staticmethod
    def _upstream_error_message(exc: APIStatusError) -> str:
        try:
            body = exc.response.json()
        except ValueError:
            return exc.response.text or exc.message

        if isinstance(body, dict):
            error = body.get("error")
            if isinstance(error, dict):
                message = error.get("message")
                if isinstance(message, str) and message:
                    return message
            if isinstance(error, str) and error:
                return error

        return exc.message
