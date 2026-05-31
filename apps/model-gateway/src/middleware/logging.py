from time import perf_counter

import structlog
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from src.utils.request_context import get_request_id

logger = structlog.get_logger(__name__)


class StructuredLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        started_at = perf_counter()

        try:
            response = await call_next(request)
        except Exception:
            latency_ms = round((perf_counter() - started_at) * 1000, 2)
            logger.exception(
                "request_failed",
                request_id=get_request_id(),
                method=request.method,
                endpoint=request.url.path,
                latency_ms=latency_ms,
            )
            raise

        latency_ms = round((perf_counter() - started_at) * 1000, 2)
        logger.info(
            "request_completed",
            request_id=get_request_id(),
            method=request.method,
            endpoint=request.url.path,
            status_code=response.status_code,
            latency_ms=latency_ms,
        )
        return response
