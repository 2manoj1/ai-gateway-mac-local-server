from dataclasses import dataclass
from typing import Annotated
from uuid import UUID

from fastapi import Depends, Header, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.core.config import get_settings
from src.core.security import api_keys_match, hash_api_key
from src.repositories.api_key_repository import ApiKeyRepository


@dataclass(frozen=True)
class AuthContext:
    api_key_id: UUID | None
    api_key_name: str


async def verify_api_key(
    request: Request,
    x_api_key: Annotated[str | None, Header(alias="X-API-Key")] = None,
    authorization: Annotated[str | None, Header(alias="Authorization")] = None,
) -> AuthContext:
    settings = get_settings()
    candidate_api_key = extract_api_key(
        x_api_key=x_api_key,
        authorization=authorization,
    )

    if candidate_api_key:
        sessionmaker = getattr(request.app.state, "db_sessionmaker", None)

        if sessionmaker is not None:
            auth_context = await verify_database_api_key(
                sessionmaker=sessionmaker,
                candidate_api_key=candidate_api_key,
            )

            if auth_context is not None:
                return auth_context

    if api_keys_match(candidate_api_key, settings.api_key):
        return AuthContext(
            api_key_id=None,
            api_key_name="env",
        )

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing API key",
    )


async def verify_admin_api_key(
    x_api_key: Annotated[str | None, Header(alias="X-API-Key")] = None,
    authorization: Annotated[str | None, Header(alias="Authorization")] = None,
) -> AuthContext:
    settings = get_settings()
    candidate_api_key = extract_api_key(
        x_api_key=x_api_key,
        authorization=authorization,
    )

    if not api_keys_match(candidate_api_key, settings.api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing admin API key",
        )

    return AuthContext(
        api_key_id=None,
        api_key_name="env",
    )


def extract_api_key(
    *,
    x_api_key: str | None,
    authorization: str | None,
) -> str | None:
    bearer_token = None

    if authorization and authorization.lower().startswith("bearer "):
        bearer_token = authorization[7:].strip()

    return x_api_key or bearer_token


async def verify_database_api_key(
    *,
    sessionmaker: async_sessionmaker[AsyncSession],
    candidate_api_key: str,
) -> AuthContext | None:
    api_key_repository = ApiKeyRepository()

    async with sessionmaker() as session:
        api_key = await api_key_repository.get_active_by_key_hash(
            session,
            hash_api_key(candidate_api_key),
        )

        if api_key is None:
            return None

        await api_key_repository.mark_last_used(session, api_key)
        await session.commit()

        return AuthContext(
            api_key_id=api_key.id,
            api_key_name=api_key.name,
        )


AuthContextDependency = Annotated[AuthContext, Depends(verify_api_key)]
AdminAuthContextDependency = Annotated[AuthContext, Depends(verify_admin_api_key)]
