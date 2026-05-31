from qdrant_client import AsyncQdrantClient

from src.core.config import Settings


def create_qdrant_client(settings: Settings) -> AsyncQdrantClient:
    return AsyncQdrantClient(url=settings.qdrant_url)
