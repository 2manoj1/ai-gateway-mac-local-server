from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints

Message = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class DirectMessageRequest(BaseModel):
    message: Message
    model: str | None = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "/no_think Reply with exactly: external-agent-ok",
                "model": "qwen3.5:9b",
            },
        },
    )


class DirectMessageResponse(BaseModel):
    response: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "response": "external-agent-ok",
            },
        },
    )
