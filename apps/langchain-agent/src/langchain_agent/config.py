from functools import lru_cache

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    production_gateway_base_url: str = "https://api.manojmukherjee.co.in"
    production_gateway_api_key: str = Field(
        default="",
        validation_alias="PRODUCTION_GATEWAY_API_KEY",
    )
    gateway_api_key: str = ""
    default_model: str = "qwen3.5:9b"
    port: int = 8001

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @model_validator(mode="after")
    def normalize(self) -> Settings:
        if not self.production_gateway_api_key and self.gateway_api_key:
            self.production_gateway_api_key = self.gateway_api_key

        self.production_gateway_base_url = self.production_gateway_base_url.rstrip("/")
        return self

    @property
    def openai_base_url(self) -> str:
        return f"{self.production_gateway_base_url}/v1"

    @property
    def chat_completions_url(self) -> str:
        return f"{self.openai_base_url}/chat/completions"


@lru_cache
def get_settings() -> Settings:
    return Settings()
