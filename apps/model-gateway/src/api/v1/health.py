from fastapi import APIRouter

from src.schemas.response import HealthResponse

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Check gateway health",
    description=(
        "Returns `ok` when the FastAPI gateway is running. No authentication required."
    ),
    operation_id="checkHealth",
    responses={
        200: {
            "description": "Gateway is reachable and healthy.",
        },
    },
)
async def health() -> HealthResponse:
    return HealthResponse(status="ok")
