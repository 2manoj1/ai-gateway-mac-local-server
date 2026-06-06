import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from inspect import signature
from typing import Any, NoReturn, cast

import httpx
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
        self._chat_semaphore = asyncio.BoundedSemaphore(
            settings.ollama_chat_concurrency_limit,
        )
        self._chat_acquire_timeout_seconds = (
            settings.ollama_chat_acquire_timeout_seconds
        )
        self._keep_alive = self._normalize_keep_alive(settings.ollama_keep_alive)
        self._client = AsyncOpenAI(
            api_key="ollama",
            base_url=settings.ollama_base_url,
            max_retries=0,
            timeout=settings.ollama_request_timeout_seconds,
            http_client=httpx.AsyncClient(
                timeout=httpx.Timeout(settings.ollama_request_timeout_seconds),
                limits=httpx.Limits(
                    max_connections=settings.ollama_http_max_connections,
                    max_keepalive_connections=(
                        settings.ollama_http_max_keepalive_connections
                    ),
                ),
            ),
        )

    async def warmup(self, model: str) -> None:
        await self._client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": ".",
                }
            ],
            max_tokens=1,
            temperature=0,
            extra_body={"keep_alive": self._keep_alive, "think": False},
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
        async with self._chat_slot():
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
        async with self._chat_slot():
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

    @asynccontextmanager
    async def _chat_slot(self) -> AsyncIterator[None]:
        try:
            await asyncio.wait_for(
                self._chat_semaphore.acquire(),
                timeout=self._chat_acquire_timeout_seconds,
            )
        except TimeoutError as exc:
            raise OllamaClientError(
                "Ollama chat concurrency limit reached; retry shortly",
                status_code=429,
                error_type="rate_limit_error",
                code="chat_concurrency_limit",
            ) from exc

        try:
            yield
        finally:
            self._chat_semaphore.release()

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
            if "keep_alive" in extra_body:
                extra_body["keep_alive"] = OllamaClient._normalize_keep_alive(
                    extra_body["keep_alive"],
                )
            kwargs["extra_body"] = extra_body

        return kwargs

    @staticmethod
    def _normalize_keep_alive(value: Any) -> Any:
        if isinstance(value, str):
            stripped = value.strip()
            if stripped.removeprefix("-").isdigit():
                return int(stripped)
        return value

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
