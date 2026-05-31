from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.api_key import ApiKey


class ApiKeyRepository:
    async def get_active_by_key_hash(
        self,
        session: AsyncSession,
        key_hash: str,
    ) -> ApiKey | None:
        statement = select(ApiKey).where(
            ApiKey.key_hash == key_hash,
            ApiKey.is_active.is_(True),
        )
        result = await session.execute(statement)
        return result.scalar_one_or_none()
