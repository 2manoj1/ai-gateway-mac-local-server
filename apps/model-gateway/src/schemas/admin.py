from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ApiKeyCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "name": "local-ui",
                }
            ]
        },
    )


class ApiKeyResponse(BaseModel):
    id: UUID
    name: str
    is_active: bool
    created_at: datetime
    last_used_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class ApiKeyCreateResponse(ApiKeyResponse):
    key: str = Field(
        description=(
            "Plaintext API key. It is shown only once and only the hash is stored."
        ),
    )


class ApiKeyListResponse(BaseModel):
    data: list[ApiKeyResponse]
