from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.api_key import ApiKey


class ApiKeyRepository:
    async def create(
        self,
        session: AsyncSession,
        *,
        name: str,
        key_hash: str,
    ) -> ApiKey:
        api_key = ApiKey(
            name=name,
            key_hash=key_hash,
            is_active=True,
        )
        session.add(api_key)
        await session.flush()
        return api_key

    async def list(
        self,
        session: AsyncSession,
        *,
        include_inactive: bool = False,
    ) -> list[ApiKey]:
        statement = select(ApiKey).order_by(ApiKey.created_at.desc())

        if not include_inactive:
            statement = statement.where(ApiKey.is_active.is_(True))

        result = await session.execute(statement)
        return list(result.scalars().all())

    async def get_by_id(
        self,
        session: AsyncSession,
        api_key_id: UUID,
    ) -> ApiKey | None:
        return await session.get(ApiKey, api_key_id)

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

    async def mark_last_used(
        self,
        session: AsyncSession,
        api_key: ApiKey,
    ) -> ApiKey:
        api_key.last_used_at = datetime.now(UTC)
        await session.flush()
        return api_key

    async def deactivate(
        self,
        session: AsyncSession,
        api_key: ApiKey,
    ) -> ApiKey:
        api_key.is_active = False
        await session.flush()
        return api_key
