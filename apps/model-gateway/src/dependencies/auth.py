from dataclasses import dataclass
from typing import Annotated
from uuid import UUID

from fastapi import Depends, Header, HTTPException, status

from src.core.config import get_settings
from src.core.security import api_keys_match


@dataclass(frozen=True)
class AuthContext:
    api_key_id: UUID | None
    api_key_name: str


async def verify_api_key(
    x_api_key: Annotated[str | None, Header(alias="X-API-Key")] = None,
    authorization: Annotated[str | None, Header(alias="Authorization")] = None,
) -> AuthContext:
    settings = get_settings()
    bearer_token = None

    if authorization and authorization.lower().startswith("bearer "):
        bearer_token = authorization[7:].strip()

    candidate_api_key = x_api_key or bearer_token

    if not api_keys_match(candidate_api_key, settings.api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )

    return AuthContext(
        api_key_id=None,
        api_key_name="env",
    )


AuthContextDependency = Annotated[AuthContext, Depends(verify_api_key)]
