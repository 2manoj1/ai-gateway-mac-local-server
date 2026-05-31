from fastapi import APIRouter, Depends, status

from src.dependencies.auth import verify_api_key

router = APIRouter(
    prefix="/rag",
    tags=["RAG"],
    dependencies=[Depends(verify_api_key)],
)


@router.get(
    "/status",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Check RAG placeholder status",
    description=(
        "Placeholder endpoint reserved for future Qdrant-backed retrieval "
        "workflows. It intentionally returns no content."
    ),
    operation_id="checkRagStatus",
    responses={
        204: {
            "description": "RAG placeholder route is registered.",
        },
        401: {
            "description": "Missing or invalid API key.",
        },
    },
)
async def rag_status() -> None:
    return None
