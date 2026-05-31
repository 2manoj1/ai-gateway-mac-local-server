from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.repositories.usage_repository import UsageRepository


class UsageLoggingService:
    def __init__(
        self,
        sessionmaker: async_sessionmaker[AsyncSession],
        usage_repository: UsageRepository,
    ) -> None:
        self._sessionmaker = sessionmaker
        self._usage_repository = usage_repository

    async def log_completion(
        self,
        *,
        api_key_id: UUID | None,
        endpoint: str,
        model: str,
        tokens_input: int = 0,
        tokens_output: int = 0,
    ) -> None:
        async with self._sessionmaker() as session:
            await self._usage_repository.create_usage_log(
                session,
                api_key_id=api_key_id,
                endpoint=endpoint,
                model=model,
                tokens_input=tokens_input,
                tokens_output=tokens_output,
            )
            await session.commit()
