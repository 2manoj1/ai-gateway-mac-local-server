from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.clients.ollama import OllamaClient
from src.core.config import Settings, get_settings
from src.dependencies.resources import get_ollama_client, get_sessionmaker
from src.repositories.api_key_repository import ApiKeyRepository
from src.repositories.usage_repository import UsageRepository
from src.services.api_key_service import ApiKeyService
from src.services.openai_service import OpenAICompatibleService
from src.services.usage_service import UsageLoggingService


def get_usage_service(
    sessionmaker: Annotated[
        async_sessionmaker[AsyncSession],
        Depends(get_sessionmaker),
    ],
) -> UsageLoggingService:
    return UsageLoggingService(
        sessionmaker=sessionmaker,
        usage_repository=UsageRepository(),
    )


def get_api_key_service() -> ApiKeyService:
    return ApiKeyService(api_key_repository=ApiKeyRepository())


def get_openai_service(
    ollama_client: Annotated[OllamaClient, Depends(get_ollama_client)],
    usage_service: Annotated[UsageLoggingService, Depends(get_usage_service)],
) -> OpenAICompatibleService:
    settings: Settings = get_settings()
    return OpenAICompatibleService(
        settings=settings,
        ollama_client=ollama_client,
        usage_service=usage_service,
    )
