from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant", "tool"]
    content: str

    model_config = ConfigDict(extra="allow")


class ChatCompletionRequest(BaseModel):
    model: str | None = None
    messages: list[ChatMessage] = Field(min_length=1)

    model_config = ConfigDict(extra="allow")


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


class ModelObject(BaseModel):
    id: str
    object: Literal["model"] = "model"
    created: int | None = None
    owned_by: str = "ollama"

    model_config = ConfigDict(extra="allow")


class ModelsResponse(BaseModel):
    object: Literal["list"] = "list"
    data: list[ModelObject]


class OpenAIError(BaseModel):
    message: str
    type: str
    param: str | None = None
    code: str | None = None


class OpenAIErrorResponse(BaseModel):
    error: OpenAIError


JsonDict = dict[str, Any]
