from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import JSONResponse, Response

_SKIP_PATHS = {"/health", "/metrics", "/docs", "/openapi.json", "/redoc"}


class ServiceAuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, expected_key: str) -> None:  # noqa: ANN001
        super().__init__(app)
        self.expected_key = expected_key

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.url.path in _SKIP_PATHS:
            return await call_next(request)

        if request.url.path.startswith("/webhooks"):
            return await call_next(request)

        key = request.headers.get("X-Service-Key")
        if key != self.expected_key:
            return JSONResponse(
                status_code=401,
                content={"error": {"code": "UNAUTHORIZED", "message": "Invalid service key", "details": {}}},
            )

        return await call_next(request)
