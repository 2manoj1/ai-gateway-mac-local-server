from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.usage_log import UsageLog


class UsageRepository:
    async def create_usage_log(
        self,
        session: AsyncSession,
        *,
        api_key_id: UUID | None,
        endpoint: str,
        model: str,
        tokens_input: int = 0,
        tokens_output: int = 0,
    ) -> UsageLog:
        usage_log = UsageLog(
            api_key_id=api_key_id,
            endpoint=endpoint,
            model=model,
            tokens_input=tokens_input,
            tokens_output=tokens_output,
        )
        session.add(usage_log)
        await session.flush()
        return usage_log
