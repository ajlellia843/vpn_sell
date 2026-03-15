import time
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request, Response
from prometheus_client import Counter, Histogram, generate_latest
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response as StarletteResponse


REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["service", "method", "path", "status"],
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency",
    ["service", "method", "path"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
)

ERROR_COUNT = Counter(
    "http_errors_total",
    "Total HTTP errors",
    ["service", "method", "path", "error_type"],
)


class MetricsMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI, service_name: str) -> None:
        super().__init__(app)
        self.service_name = service_name

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[StarletteResponse]],
    ) -> StarletteResponse:
        if request.url.path in ("/metrics", "/health"):
            return await call_next(request)

        path = request.url.path
        method = request.method
        start = time.perf_counter()

        try:
            response = await call_next(request)
        except Exception:
            ERROR_COUNT.labels(
                service=self.service_name,
                method=method,
                path=path,
                error_type="unhandled_exception",
            ).inc()
            raise

        duration = time.perf_counter() - start
        status = str(response.status_code)

        REQUEST_COUNT.labels(service=self.service_name, method=method, path=path, status=status).inc()
        REQUEST_LATENCY.labels(service=self.service_name, method=method, path=path).observe(duration)

        if response.status_code >= 400:
            ERROR_COUNT.labels(
                service=self.service_name, method=method, path=path, error_type=f"http_{status}"
            ).inc()

        return response


def metrics_endpoint(_request: Request) -> Response:
    return Response(content=generate_latest(), media_type="text/plain; charset=utf-8")


def setup_metrics(app: FastAPI, service_name: str) -> None:
    app.add_middleware(MetricsMiddleware, service_name=service_name)
    app.add_route("/metrics", metrics_endpoint, methods=["GET"])
