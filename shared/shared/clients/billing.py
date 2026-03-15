from typing import Any

from shared.clients.base import BaseHTTPClient


class BillingServiceClient(BaseHTTPClient):
    async def list_plans(self) -> list[dict[str, Any]]:
        return await self.get("/plans/")

    async def get_plan(self, plan_id: str) -> dict[str, Any]:
        return await self.get(f"/plans/{plan_id}")

    async def create_plan(self, data: dict[str, Any]) -> dict[str, Any]:
        return await self.post("/plans/", json=data)

    async def update_plan(self, plan_id: str, data: dict[str, Any]) -> dict[str, Any]:
        return await self.put(f"/plans/{plan_id}", json=data)

    async def create_order(self, user_id: str, plan_id: str) -> dict[str, Any]:
        return await self.post("/orders/", json={"user_id": user_id, "plan_id": plan_id})

    async def get_order(self, order_id: str) -> dict[str, Any]:
        return await self.get(f"/orders/{order_id}")

    async def list_orders_by_user(self, user_id: str) -> list[dict[str, Any]]:
        return await self.get(f"/orders/user/{user_id}")

    async def list_orders(self, offset: int = 0, limit: int = 50, status: str | None = None) -> dict[str, Any]:
        params: dict[str, Any] = {"offset": offset, "limit": limit}
        if status:
            params["status"] = status
        return await self.get("/orders/", params=params)

    async def get_active_subscription(self, user_id: str) -> dict[str, Any] | None:
        try:
            return await self.get(f"/subscriptions/user/{user_id}/active")
        except Exception:
            return None

    async def get_subscription(self, subscription_id: str) -> dict[str, Any]:
        return await self.get(f"/subscriptions/{subscription_id}")

    async def list_subscriptions(self, offset: int = 0, limit: int = 50, status: str | None = None) -> dict[str, Any]:
        params: dict[str, Any] = {"offset": offset, "limit": limit}
        if status:
            params["status"] = status
        return await self.get("/subscriptions/", params=params)

    async def extend_subscription(self, subscription_id: str, days: int) -> dict[str, Any]:
        return await self.post(f"/subscriptions/{subscription_id}/extend", json={"days": days})

    async def revoke_subscription(self, subscription_id: str) -> dict[str, Any]:
        return await self.post(f"/subscriptions/{subscription_id}/revoke")
