from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_db_session
from src.dependencies.auth import AdminAuthContextDependency
from src.dependencies.services import get_api_key_service
from src.schemas.admin import (
    ApiKeyCreateRequest,
    ApiKeyCreateResponse,
    ApiKeyListResponse,
    ApiKeyResponse,
)
from src.services.api_key_service import ApiKeyService

router = APIRouter(
    prefix="/api-keys",
    tags=["Admin"],
)


@router.post(
    "",
    response_model=ApiKeyCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create an API key",
    description=(
        "Creates a PostgreSQL-backed API key. The plaintext key is returned "
        "only once; the database stores only its SHA-256 hash."
    ),
    operation_id="createApiKey",
    responses={
        201: {
            "description": "API key created. Store the `key` value securely.",
        },
        401: {
            "description": "Missing or invalid admin API key.",
        },
    },
)
async def create_api_key(
    request: ApiKeyCreateRequest,
    auth_context: AdminAuthContextDependency,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    api_key_service: Annotated[ApiKeyService, Depends(get_api_key_service)],
) -> ApiKeyCreateResponse:
    _ = auth_context
    api_key, plain_key = await api_key_service.create_api_key(
        session,
        name=request.name,
    )
    await session.commit()

    return ApiKeyCreateResponse(
        id=api_key.id,
        name=api_key.name,
        is_active=api_key.is_active,
        created_at=api_key.created_at,
        last_used_at=api_key.last_used_at,
        key=plain_key,
    )


@router.get(
    "",
    response_model=ApiKeyListResponse,
    summary="List API keys",
    description="Lists PostgreSQL-backed API keys without exposing key hashes.",
    operation_id="listApiKeys",
    responses={
        200: {
            "description": "API keys returned.",
        },
        401: {
            "description": "Missing or invalid admin API key.",
        },
    },
)
async def list_api_keys(
    auth_context: AdminAuthContextDependency,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    api_key_service: Annotated[ApiKeyService, Depends(get_api_key_service)],
    include_inactive: Annotated[
        bool,
        Query(description="Include inactive API keys in the response."),
    ] = False,
) -> ApiKeyListResponse:
    _ = auth_context
    api_keys = await api_key_service.list_api_keys(
        session,
        include_inactive=include_inactive,
    )
    return ApiKeyListResponse(
        data=[ApiKeyResponse.model_validate(api_key) for api_key in api_keys]
    )


@router.delete(
    "/{api_key_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deactivate an API key",
    description=(
        "Soft-deletes an API key by setting `is_active=false`. Existing usage "
        "logs remain linked for audit history."
    ),
    operation_id="deleteApiKey",
    responses={
        204: {
            "description": "API key deactivated.",
        },
        401: {
            "description": "Missing or invalid admin API key.",
        },
        404: {
            "description": "API key not found.",
        },
    },
)
async def delete_api_key(
    api_key_id: UUID,
    auth_context: AdminAuthContextDependency,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    api_key_service: Annotated[ApiKeyService, Depends(get_api_key_service)],
) -> Response:
    _ = auth_context
    deleted = await api_key_service.deactivate_api_key(session, api_key_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found",
        )

    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
