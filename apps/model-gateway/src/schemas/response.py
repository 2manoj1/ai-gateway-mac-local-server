from pydantic import BaseModel, ConfigDict


class HealthResponse(BaseModel):
    status: str

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "status": "ok",
                }
            ]
        },
    )


class ModelInfo(BaseModel):
    id: str
    object: str | None = None
    created: int | None = None
    owned_by: str | None = None


class ModelsResponse(BaseModel):
    models: list[ModelInfo]

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "models": [
                    {
                        "id": "qwen3.5:9b",
                        "object": "model",
                        "created": None,
                        "owned_by": "ollama",
                    },
                ],
            },
        },
    )


class ErrorResponse(BaseModel):
    detail: str
