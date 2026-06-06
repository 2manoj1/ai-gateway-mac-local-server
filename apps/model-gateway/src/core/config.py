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
    internal_gateway_base_url: str = "http://127.0.0.1:8000"
    ollama_warmup_on_startup: bool = True
    ollama_keep_alive: int | str = -1
    ollama_chat_concurrency_limit: int = 10
    ollama_chat_acquire_timeout_seconds: float = 0.25
    ollama_request_timeout_seconds: float = 300.0
    ollama_http_max_connections: int = 20
    ollama_http_max_keepalive_connections: int = 10
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
        if isinstance(self.ollama_keep_alive, str) and not self.ollama_keep_alive:
            raise ValueError("OLLAMA_KEEP_ALIVE is required")
        if self.ollama_chat_concurrency_limit < 1:
            raise ValueError("OLLAMA_CHAT_CONCURRENCY_LIMIT must be at least 1")
        if self.ollama_chat_acquire_timeout_seconds <= 0:
            raise ValueError("OLLAMA_CHAT_ACQUIRE_TIMEOUT_SECONDS must be positive")
        if self.ollama_request_timeout_seconds <= 0:
            raise ValueError("OLLAMA_REQUEST_TIMEOUT_SECONDS must be positive")
        if self.ollama_http_max_connections < self.ollama_chat_concurrency_limit:
            raise ValueError(
                "OLLAMA_HTTP_MAX_CONNECTIONS must be greater than or equal to "
                "OLLAMA_CHAT_CONCURRENCY_LIMIT"
            )
        if self.ollama_http_max_keepalive_connections < 1:
            raise ValueError("OLLAMA_HTTP_MAX_KEEPALIVE_CONNECTIONS must be at least 1")
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
