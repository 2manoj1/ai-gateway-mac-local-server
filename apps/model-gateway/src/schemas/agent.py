from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints

DirectMessage = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class DirectMessageRequest(BaseModel):
    message: DirectMessage
    model: str | None = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "hello",
                "model": "qwen3.5:9b",
            },
        },
    )
