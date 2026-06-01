from collections.abc import Sequence
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, model_validator


class ChatMessage(BaseModel):
    role: str
    content: Any = None

    model_config = ConfigDict(
        extra="allow",
        json_schema_extra={
            "examples": [
                {
                    "role": "user",
                    "content": "hello",
                }
            ]
        },
    )


class ChatCompletionRequest(BaseModel):
    model: str | None = None
    messages: list[ChatMessage] | None = None
    prompt: str | None = None
    stream: bool = False

    model_config = ConfigDict(
        extra="allow",
        json_schema_extra={
            "examples": [
                {
                    "model": "qwen3.5:9b",
                    "messages": [
                        {
                            "role": "user",
                            "content": "hello",
                        }
                    ],
                    "stream": False,
                },
                {
                    "model": "qwen3.5:9b",
                    "messages": [
                        {
                            "role": "user",
                            "content": "Write one sentence about local AI.",
                        }
                    ],
                    "stream": True,
                },
            ]
        },
    )

    @model_validator(mode="after")
    def validate_messages_or_prompt(self) -> ChatCompletionRequest:
        if not self.messages and self.prompt is None:
            raise ValueError("Either messages or prompt is required")
        return self


class CompletionRequest(BaseModel):
    model: str | None = None
    prompt: str | Sequence[str] | Sequence[int] | Sequence[Sequence[int]]
    stream: bool = False

    model_config = ConfigDict(
        extra="allow",
        json_schema_extra={
            "examples": [
                {
                    "model": "qwen3.5:9b",
                    "prompt": "Write one sentence about local AI.",
                    "stream": False,
                }
            ]
        },
    )


class EmbeddingRequest(BaseModel):
    model: str | None = None
    input: str | Sequence[str] | Sequence[int] | Sequence[Sequence[int]]

    model_config = ConfigDict(
        extra="allow",
        json_schema_extra={
            "examples": [
                {
                    "model": "nomic-embed-text",
                    "input": "hello",
                }
            ]
        },
    )


class ResponseRequest(BaseModel):
    model: str | None = None
    input: Any = None
    stream: bool = False

    model_config = ConfigDict(
        extra="allow",
        json_schema_extra={
            "examples": [
                {
                    "model": "qwen3.5:9b",
                    "input": "hello",
                    "stream": False,
                }
            ]
        },
    )


class ImageGenerationRequest(BaseModel):
    model: str | None = None
    prompt: str
    stream: bool = False

    model_config = ConfigDict(
        extra="allow",
        json_schema_extra={
            "examples": [
                {
                    "model": "x/z-image-turbo",
                    "prompt": "A robot painting",
                    "size": "1024x1024",
                    "response_format": "b64_json",
                }
            ]
        },
    )


class ChatCompletionMessage(BaseModel):
    role: Literal["assistant"] = "assistant"
    content: Any = None


class ChatCompletionChoice(BaseModel):
    index: int
    message: ChatCompletionMessage
    finish_reason: str


class ChatCompletionResponse(BaseModel):
    id: str
    object: Literal["chat.completion"] = "chat.completion"
    created: int
    model: str
    choices: list[ChatCompletionChoice]

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "id": "chatcmpl-0f5c7f0c6f2b4c01a54f495f7fcd929a",
                    "object": "chat.completion",
                    "created": 1780200000,
                    "model": "qwen3.5:9b",
                    "choices": [
                        {
                            "index": 0,
                            "message": {
                                "role": "assistant",
                                "content": "hello",
                            },
                            "finish_reason": "stop",
                        }
                    ],
                }
            ]
        },
    )


class ChatCompletionChunkDelta(BaseModel):
    role: Literal["assistant"] | None = None
    content: str | None = None


class ChatCompletionChunkChoice(BaseModel):
    index: int
    delta: ChatCompletionChunkDelta
    finish_reason: str | None = None


class ChatCompletionChunk(BaseModel):
    id: str
    object: Literal["chat.completion.chunk"] = "chat.completion.chunk"
    created: int
    model: str
    choices: list[ChatCompletionChunkChoice]

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "id": "chatcmpl-0f5c7f0c6f2b4c01a54f495f7fcd929a",
                    "object": "chat.completion.chunk",
                    "created": 1780200000,
                    "model": "qwen3.5:9b",
                    "choices": [
                        {
                            "index": 0,
                            "delta": {
                                "content": "hel",
                            },
                            "finish_reason": None,
                        }
                    ],
                }
            ]
        },
    )


class ModelObject(BaseModel):
    id: str
    object: Literal["model"] = "model"
    created: int | None = None
    owned_by: str = "ollama"

    model_config = ConfigDict(extra="allow")


class ModelsResponse(BaseModel):
    object: Literal["list"] = "list"
    data: list[ModelObject]

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "object": "list",
                    "data": [
                        {
                            "id": "qwen3.5:9b",
                            "object": "model",
                            "created": 1780200000,
                            "owned_by": "library",
                        }
                    ],
                }
            ]
        },
    )


class OpenAIError(BaseModel):
    message: str
    type: str
    param: str | None = None
    code: str | None = None


class OpenAIErrorResponse(BaseModel):
    error: OpenAIError

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "error": {
                        "message": "Invalid or missing API key",
                        "type": "authentication_error",
                        "param": None,
                        "code": "unauthorized",
                    }
                }
            ]
        },
    )


JsonDict = dict[str, Any]
