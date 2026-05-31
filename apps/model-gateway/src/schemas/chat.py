from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints

Prompt = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class ChatRequest(BaseModel):
    prompt: Prompt

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "prompt": "hello",
            },
        },
    )


class ChatResponse(BaseModel):
    response: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "response": "hello",
            },
        },
    )
