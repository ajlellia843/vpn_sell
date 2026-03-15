from __future__ import annotations

from typing import Any

import httpx
import structlog

logger = structlog.get_logger(__name__)


class APIError(Exception):
    def __init__(self, status_code: int, detail: str = "") -> None:
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"API error {status_code}: {detail}")


class APIClient:
    def __init__(self, base_url: str, api_key: str) -> None:
        self._client = httpx.AsyncClient(
            base_url=base_url,
            timeout=15.0,
            headers={"X-Service-Key": api_key},
        )

    async def close(self) -> None:
        await self._client.aclose()

    async def _request(
        self,
        method: str,
        path: str,
        *,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> Any:
        try:
            resp = await self._client.request(method, path, json=json, params=params)
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPStatusError as exc:
            detail = ""
            try:
                detail = exc.response.text
            except Exception:
                pass
            logger.error(
                "api_request_failed",
                method=method,
                path=path,
                status=exc.response.status_code,
                detail=detail,
            )
            raise APIError(exc.response.status_code, detail) from exc
        except httpx.RequestError as exc:
            logger.error("api_request_error", method=method, path=path, error=str(exc))
            raise APIError(0, str(exc)) from exc

    async def get_me(
        self,
        telegram_id: int,
        username: str | None = None,
        first_name: str | None = None,
    ) -> dict[str, Any]:
        return await self._request(
            "POST",
            "/bot/me",
            json={
                "telegram_id": telegram_id,
                "username": username,
                "first_name": first_name,
            },
        )

    async def get_plans(self) -> list[dict[str, Any]]:
        return await self._request("GET", "/bot/plans")

    async def create_order(
        self, telegram_id: int, plan_id: str
    ) -> dict[str, Any]:
        return await self._request(
            "POST",
            "/bot/orders",
            json={"telegram_id": telegram_id, "plan_id": plan_id},
        )

    async def get_order(self, order_id: str) -> dict[str, Any]:
        return await self._request("GET", f"/bot/orders/{order_id}")

    async def get_subscription(self, telegram_id: int) -> dict[str, Any]:
        return await self._request(
            "GET", "/bot/subscription", params={"telegram_id": telegram_id}
        )

    async def extend_subscription(
        self, telegram_id: int, days: int
    ) -> dict[str, Any]:
        return await self._request(
            "POST",
            "/bot/subscription/extend",
            json={"telegram_id": telegram_id, "days": days},
        )
