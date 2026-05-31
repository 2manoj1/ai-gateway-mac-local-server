from uuid import uuid4

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from src.utils.request_context import request_id_context

REQUEST_ID_HEADER = "X-Request-ID"


class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        request_id = request.headers.get(REQUEST_ID_HEADER, str(uuid4()))
        token = request_id_context.set(request_id)

        try:
            response = await call_next(request)
        finally:
            request_id_context.reset(token)

        response.headers[REQUEST_ID_HEADER] = request_id
        return response
