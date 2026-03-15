from typing import Any

import httpx
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential

from shared.exceptions import NotFoundError, ServiceError

logger = structlog.get_logger()


class BaseHTTPClient:
    def __init__(self, base_url: str, service_api_key: str, timeout: float = 10.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._api_key = service_api_key
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self._base_url,
                timeout=self._timeout,
                headers={"X-Service-Key": self._api_key},
            )
        return self._client

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    def _handle_error(self, response: httpx.Response) -> None:
        if response.status_code == 404:
            data = response.json()
            msg = data.get("error", {}).get("message", "Not found")
            raise NotFoundError(msg)
        if response.status_code >= 400:
            try:
                data = response.json()
                msg = data.get("error", {}).get("message", response.text)
            except Exception:
                msg = response.text
            raise ServiceError(msg)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.5, max=5))
    async def _request(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        client = await self._get_client()
        response = await client.request(method, path, **kwargs)
        self._handle_error(response)
        if response.status_code == 204:
            return {}
        return response.json()

    async def get(self, path: str, **kwargs: Any) -> dict[str, Any]:
        return await self._request("GET", path, **kwargs)

    async def post(self, path: str, **kwargs: Any) -> dict[str, Any]:
        return await self._request("POST", path, **kwargs)

    async def put(self, path: str, **kwargs: Any) -> dict[str, Any]:
        return await self._request("PUT", path, **kwargs)

    async def patch(self, path: str, **kwargs: Any) -> dict[str, Any]:
        return await self._request("PATCH", path, **kwargs)

    async def delete(self, path: str, **kwargs: Any) -> dict[str, Any]:
        return await self._request("DELETE", path, **kwargs)
