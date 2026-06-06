import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

import structlog
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from src.api.admin.api_keys import router as admin_api_keys_router
from src.api.openai.chat_completions import router as chat_completions_router
from src.api.openai.completions import router as completions_router
from src.api.openai.embeddings import router as embeddings_router
from src.api.openai.images import router as images_router
from src.api.openai.models import router as openai_models_router
from src.api.openai.responses import router as responses_router
from src.api.v1.agent import router as agent_router
from src.api.v1.health import router as health_router
from src.api.v1.rag import router as rag_router
from src.clients.ollama import OllamaClient, OllamaClientError
from src.clients.qdrant import create_qdrant_client
from src.clients.redis import create_redis_client
from src.core.config import Settings, get_settings
from src.core.logging import configure_logging
from src.core.openapi import (
    OPENAPI_DESCRIPTION,
    OPENAPI_TAGS,
    apply_openapi_customizations,
)
from src.db.session import create_engine, create_sessionmaker
from src.middleware.logging import StructuredLoggingMiddleware
from src.middleware.request_id import RequestIdMiddleware
from src.schemas.openai import OpenAIError, OpenAIErrorResponse

settings = get_settings()
configure_logging(settings.log_level)
logger = structlog.get_logger(__name__)


def openai_error_response(
    *,
    status_code: int,
    message: str,
    error_type: str,
    code: str | None = None,
) -> JSONResponse:
    error = OpenAIErrorResponse(
        error=OpenAIError(
            message=message,
            type=error_type,
            code=code,
        ),
    )
    return JSONResponse(
        status_code=status_code,
        content=error.model_dump(),
    )


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    db_engine = create_engine(settings)
    db_sessionmaker = create_sessionmaker(db_engine)
    ollama_client = OllamaClient(settings)
    redis_client = create_redis_client(settings)
    qdrant_client = create_qdrant_client(settings)

    app.state.db_engine = db_engine
    app.state.db_sessionmaker = db_sessionmaker
    app.state.ollama_client = ollama_client
    app.state.redis_client = redis_client
    app.state.qdrant_client = qdrant_client

    if settings.ollama_warmup_on_startup:
        await ollama_client.warmup(
            model=settings.default_model,
        )

    logger.info(
        "application_started",
        app_name=settings.app_name,
        environment=settings.environment,
        default_model=settings.default_model,
        chat_concurrency_limit=settings.ollama_chat_concurrency_limit,
    )

    try:
        yield
    finally:
        async with asyncio.TaskGroup() as task_group:
            task_group.create_task(ollama_client.close())
            task_group.create_task(redis_client.aclose())
            task_group.create_task(qdrant_client.close())

        await db_engine.dispose()
        logger.info("application_stopped", app_name=settings.app_name)


class DeveloperFriendlyFastAPI(FastAPI):
    def openapi(self) -> dict[str, Any]:
        if self.openapi_schema:
            return self.openapi_schema

        openapi_schema = get_openapi(
            title=self.title,
            version=self.version,
            summary=self.summary,
            description=self.description,
            routes=self.routes,
            tags=self.openapi_tags,
        )
        self.openapi_schema = apply_openapi_customizations(openapi_schema)
        return self.openapi_schema


def create_app(app_settings: Settings) -> FastAPI:
    app = DeveloperFriendlyFastAPI(
        title=app_settings.app_name,
        summary="Local OpenAI-compatible gateway for Ollama-backed model traffic.",
        description=OPENAPI_DESCRIPTION,
        version=app_settings.app_version,
        contact={
            "name": "Manoj Mukherjee - AI Gateway Local Mac Server for Research",
            "url": "https://github.com/2manoj1/ai-gateway-mac-local-server",
            "email": "info@manojmukherjee.co.in",
        },
        license_info={
            "name": "MIT",
            "identifier": "MIT",
        },
        openapi_tags=OPENAPI_TAGS,
        lifespan=lifespan,
    )

    app.add_middleware(StructuredLoggingMiddleware)
    app.add_middleware(RequestIdMiddleware)

    app.include_router(health_router, prefix=app_settings.api_v1_prefix)
    app.include_router(rag_router, prefix=app_settings.api_v1_prefix)
    app.include_router(agent_router, prefix=app_settings.api_v1_prefix)
    app.include_router(openai_models_router, prefix="/v1")
    app.include_router(chat_completions_router, prefix="/v1")
    app.include_router(completions_router, prefix="/v1")
    app.include_router(embeddings_router, prefix="/v1")
    app.include_router(responses_router, prefix="/v1")
    app.include_router(images_router, prefix="/v1")
    app.include_router(admin_api_keys_router, prefix="/admin")

    return app


app = create_app(settings)


@app.exception_handler(OllamaClientError)
async def ollama_client_exception_handler(
    request: Request,
    exc: OllamaClientError,
) -> JSONResponse:
    logger.exception(
        "ollama_client_error",
        endpoint=request.url.path,
        error=str(exc),
    )
    return openai_error_response(
        status_code=exc.status_code,
        message=str(exc),
        error_type=exc.error_type,
        code=exc.code,
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(
    request: Request,
    exc: HTTPException,
) -> JSONResponse:
    _ = request
    message = exc.detail if isinstance(exc.detail, str) else "Request failed"
    error_type = (
        "authentication_error"
        if exc.status_code == status.HTTP_401_UNAUTHORIZED
        else "invalid_request_error"
    )
    code = (
        "unauthorized"
        if exc.status_code == status.HTTP_401_UNAUTHORIZED
        else str(exc.status_code)
    )
    return openai_error_response(
        status_code=exc.status_code,
        message=message,
        error_type=error_type,
        code=code,
    )


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    _ = request
    return openai_error_response(
        status_code=status.HTTP_400_BAD_REQUEST,
        message="Invalid request body",
        error_type="invalid_request_error",
        code="invalid_request",
    )


@app.exception_handler(SQLAlchemyError)
async def database_exception_handler(
    request: Request,
    exc: SQLAlchemyError,
) -> JSONResponse:
    logger.exception(
        "database_error",
        endpoint=request.url.path,
        error=str(exc),
    )
    return openai_error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        message="Database operation failed",
        error_type="database_error",
        code="internal_error",
    )
