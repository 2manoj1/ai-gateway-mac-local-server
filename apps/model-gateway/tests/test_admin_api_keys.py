from collections.abc import AsyncGenerator
from http import HTTPStatus

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from src.core.config import get_settings
from src.db.base import Base
from src.db.session import create_engine, create_sessionmaker
from src.main import app


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


@pytest.mark.asyncio
async def test_admin_api_key_create_list_and_delete() -> None:
    settings = get_settings()

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        create_response = await client.post(
            "/admin/api-keys",
            headers={
                "X-Admin-Secret": settings.admin_secret,
            },
            json={
                "name": "test-key",
            },
        )

        assert create_response.status_code == HTTPStatus.CREATED

        payload = create_response.json()

        assert payload["id"]
        assert payload["name"] == "test-key"
        assert payload["is_active"] is True
        assert payload["key"].startswith("sk_")

        list_response = await client.get(
            "/admin/api-keys",
            headers={
                "X-Admin-Secret": settings.admin_secret,
            },
        )

        assert list_response.status_code == HTTPStatus.OK

        assert any(item["id"] == payload["id"] for item in list_response.json()["data"])

        delete_response = await client.delete(
            f"/admin/api-keys/{payload['id']}",
            headers={
                "X-Admin-Secret": settings.admin_secret,
            },
        )

        assert delete_response.status_code == HTTPStatus.NO_CONTENT

        list_after_delete = await client.get(
            "/admin/api-keys",
            headers={
                "X-Admin-Secret": settings.admin_secret,
            },
        )

        assert list_after_delete.status_code == HTTPStatus.OK

        assert all(
            item["id"] != payload["id"] for item in list_after_delete.json()["data"]
        )


@pytest.mark.asyncio
async def test_admin_api_key_requires_admin_secret() -> None:
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        response = await client.post(
            "/admin/api-keys",
            headers={
                "X-Admin-Secret": "wrong-secret",
            },
            json={
                "name": "test-key",
            },
        )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json()["detail"] == "Invalid or missing admin secret"
