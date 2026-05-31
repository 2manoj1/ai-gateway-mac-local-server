from collections.abc import AsyncGenerator
from secrets import token_urlsafe

import pytest
import pytest_asyncio
from src.core.config import get_settings
from src.core.security import hash_api_key
from src.db.base import Base
from src.db.models.api_key import ApiKey
from src.db.session import create_engine, create_sessionmaker
from src.dependencies.auth import extract_api_key, verify_database_api_key
from src.main import app
from src.repositories.api_key_repository import ApiKeyRepository


@pytest_asyncio.fixture(scope="module", autouse=True)
async def initialize_db_state() -> AsyncGenerator[None]:

    settings = get_settings()

    engine = create_engine(settings)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    sessionmaker = create_sessionmaker(engine)

    app.state.db_sessionmaker = sessionmaker
    app.state.db_engine = engine

    yield

    await engine.dispose()


def test_extract_api_key_prefers_x_api_key() -> None:
    api_key = extract_api_key(
        x_api_key="sk-header",
        authorization="Bearer sk-bearer",
    )

    assert api_key == "sk-header"


def test_extract_api_key_accepts_bearer_token() -> None:
    api_key = extract_api_key(
        x_api_key=None,
        authorization="Bearer sk-bearer",
    )

    assert api_key == "sk-bearer"


def test_extract_api_key_ignores_non_bearer_authorization() -> None:
    api_key = extract_api_key(
        x_api_key=None,
        authorization="Basic abc",
    )

    assert api_key is None


@pytest.mark.asyncio
async def test_verify_database_api_key_updates_last_used_at() -> None:
    plain_key = f"sk_{token_urlsafe(32)}"
    sessionmaker = app.state.db_sessionmaker

    async with sessionmaker() as session:
        api_key = await ApiKeyRepository().create(
            session,
            name="test-db-key",
            key_hash=hash_api_key(plain_key),
        )

        await session.commit()

        api_key_id = api_key.id

    auth_context = await verify_database_api_key(
        sessionmaker=sessionmaker,
        candidate_api_key=plain_key,
    )

    assert auth_context is not None
    assert auth_context.api_key_name == "test-db-key"
    assert auth_context.api_key_id == api_key_id

    async with sessionmaker() as session:
        stored_api_key = await session.get(
            ApiKey,
            api_key_id,
        )

        assert stored_api_key is not None
        assert stored_api_key.last_used_at is not None

        await session.delete(stored_api_key)
        await session.commit()
