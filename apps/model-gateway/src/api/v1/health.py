from fastapi import APIRouter, Depends

from src.dependencies.auth import verify_api_key
from src.schemas.response import HealthResponse

router = APIRouter(
    tags=["Health"],
    dependencies=[Depends(verify_api_key)],
)


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Check gateway health",
    description=(
        "Returns `ok` when the FastAPI gateway is running and authentication passes."
    ),
    operation_id="checkHealth",
    responses={
        200: {
            "description": "Gateway is reachable.",
        },
        401: {
            "description": "Missing or invalid API key.",
        },
    },
)
async def health() -> HealthResponse:
    return HealthResponse(status="ok")
