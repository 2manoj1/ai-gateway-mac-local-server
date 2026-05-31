from typing import cast

from fastapi import Request
from qdrant_client import AsyncQdrantClient
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.clients.ollama import OllamaClient


def get_ollama_client(request: Request) -> OllamaClient:
    return cast(OllamaClient, request.app.state.ollama_client)


def get_redis_client(request: Request) -> Redis:
    return cast(Redis, request.app.state.redis_client)


def get_qdrant_client(request: Request) -> AsyncQdrantClient:
    return cast(AsyncQdrantClient, request.app.state.qdrant_client)


def get_sessionmaker(request: Request) -> async_sessionmaker[AsyncSession]:
    return cast(async_sessionmaker[AsyncSession], request.app.state.db_sessionmaker)
