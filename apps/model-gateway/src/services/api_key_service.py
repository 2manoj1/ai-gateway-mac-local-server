from secrets import token_urlsafe
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.security import hash_api_key
from src.db.models.api_key import ApiKey
from src.repositories.api_key_repository import ApiKeyRepository


class ApiKeyService:
    def __init__(self, api_key_repository: ApiKeyRepository) -> None:
        self._api_key_repository = api_key_repository

    def generate_api_key(self) -> str:
        # Format: sk_<token>
        return f"sk_{token_urlsafe(32)}"

    async def create_api_key(
        self,
        session: AsyncSession,
        *,
        name: str,
    ) -> tuple[ApiKey, str]:
        plain_key = self.generate_api_key()
        api_key = await self._api_key_repository.create(
            session,
            name=name,
            key_hash=hash_api_key(plain_key),
        )
        return api_key, plain_key

    async def validate_api_key(
        self,
        session: AsyncSession,
        *,
        candidate_api_key: str,
    ) -> ApiKey | None:
        key_hash = hash_api_key(candidate_api_key)
        return await self._api_key_repository.get_active_by_key_hash(session, key_hash)

    async def list_api_keys(
        self,
        session: AsyncSession,
        *,
        include_inactive: bool = False,
    ) -> list[ApiKey]:
        return await self._api_key_repository.list(
            session,
            include_inactive=include_inactive,
        )

    async def deactivate_api_key(
        self,
        session: AsyncSession,
        api_key_id: UUID,
    ) -> bool:
        api_key = await self._api_key_repository.get_by_id(session, api_key_id)

        if api_key is None:
            return False

        if not api_key.is_active:
            return True

        await self._api_key_repository.deactivate(session, api_key)
        return True
