from fastapi import APIRouter, Depends, status

from src.dependencies.auth import verify_api_key

router = APIRouter(
    prefix="/rag",
    tags=["RAG"],
    dependencies=[Depends(verify_api_key)],
)


@router.get("/status", status_code=status.HTTP_204_NO_CONTENT)
async def rag_status() -> None:
    return None
