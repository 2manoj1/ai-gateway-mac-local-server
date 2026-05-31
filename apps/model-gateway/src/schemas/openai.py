from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant", "tool"]
    content: str

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
    messages: list[ChatMessage] = Field(min_length=1)
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


class ChatCompletionMessage(BaseModel):
    role: Literal["assistant"] = "assistant"
    content: str


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
