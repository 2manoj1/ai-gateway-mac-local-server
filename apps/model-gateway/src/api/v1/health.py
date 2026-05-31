from fastapi import APIRouter, Depends

from src.dependencies.auth import verify_api_key
from src.schemas.response import HealthResponse

router = APIRouter(
    tags=["Health"],
    dependencies=[Depends(verify_api_key)],
)


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok")
