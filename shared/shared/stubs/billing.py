"""Stub implementation of BillingServiceClientProtocol."""

from typing import Any

from shared.stubs.fixtures import stub_order, stub_plan, stub_subscription


class StubBillingServiceClient:
    """Returns minimal fixture data for billing_service. No HTTP calls."""

    async def list_plans(self) -> list[dict[str, Any]]:
        return [stub_plan()]

    async def get_plan(self, plan_id: str) -> dict[str, Any]:
        return stub_plan()

    async def create_plan(self, data: dict[str, Any]) -> dict[str, Any]:
        p = stub_plan()
        p.update(data)
        return p

    async def update_plan(self, plan_id: str, data: dict[str, Any]) -> dict[str, Any]:
        return stub_plan()

    async def create_order(self, user_id: str, plan_id: str) -> dict[str, Any]:
        return stub_order(user_id=user_id, plan_id=plan_id)

    async def get_order(self, order_id: str) -> dict[str, Any]:
        return stub_order()

    async def list_orders_by_user(self, user_id: str) -> list[dict[str, Any]]:
        return [stub_order(user_id=user_id)]

    async def list_orders(
        self,
        offset: int = 0,
        limit: int = 50,
        status: str | None = None,
    ) -> dict[str, Any]:
        return {"items": [stub_order()], "total": 1}

    async def get_active_subscription(self, user_id: str) -> dict[str, Any] | None:
        return stub_subscription(user_id=user_id)

    async def get_subscription(self, subscription_id: str) -> dict[str, Any]:
        return stub_subscription()

    async def list_subscriptions(
        self,
        offset: int = 0,
        limit: int = 50,
        status: str | None = None,
    ) -> dict[str, Any]:
        return {"items": [stub_subscription()], "total": 1}

    async def extend_subscription(self, subscription_id: str, days: int) -> dict[str, Any]:
        return stub_subscription()

    async def revoke_subscription(self, subscription_id: str) -> dict[str, Any]:
        s = stub_subscription()
        s["status"] = "cancelled"
        return s

    async def close(self) -> None:
        pass
