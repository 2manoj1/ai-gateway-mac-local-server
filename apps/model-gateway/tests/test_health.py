from http import HTTPStatus

import pytest
from httpx import ASGITransport, AsyncClient
from src.core.config import get_settings
from src.main import app


@pytest.mark.asyncio
async def test_health_requires_api_key() -> None:
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/api/v1/health")

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {"detail": "Invalid or missing API key"}


@pytest.mark.asyncio
async def test_health_accepts_valid_api_key() -> None:
    settings = get_settings()
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get(
            "/api/v1/health",
            headers={"X-API-Key": settings.api_key},
        )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_health_accepts_openai_bearer_token() -> None:
    settings = get_settings()
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get(
            "/api/v1/health",
            headers={"Authorization": f"Bearer {settings.api_key}"},
        )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"status": "ok"}
