from functools import lru_cache
from pathlib import Path
from typing import Self

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    admin_secret: str = ""
    database_url: str = (
        "postgresql+psycopg://aigateway:change-me-later@localhost:5432/aigateway"
    )
    redis_url: str = "redis://localhost:6379/0"
    qdrant_url: str = "http://localhost:6333"
    ollama_base_url: str = "http://localhost:11434/v1"
    ollama_warmup_on_startup: bool = True
    default_model: str = "qwen3.5:9b"

    app_name: str = "Gateway API"
    app_version: str = "0.1.0"
    api_v1_prefix: str = "/api/v1"
    environment: str = "local"
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[2] / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @model_validator(mode="after")
    def validate_required_settings(self) -> Self:
        if not self.admin_secret:
            raise ValueError("ADMIN_SECRET is required")
        if not self.database_url:
            raise ValueError("DATABASE_URL is required")
        if not self.redis_url:
            raise ValueError("REDIS_URL is required")
        if not self.qdrant_url:
            raise ValueError("QDRANT_URL is required")
        if not self.ollama_base_url:
            raise ValueError("OLLAMA_BASE_URL is required")
        if not self.default_model:
            raise ValueError("DEFAULT_MODEL is required")
        if not self.app_name:
            raise ValueError("APP_NAME is required")
        if not self.environment:
            raise ValueError("ENVIRONMENT is required")

        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
