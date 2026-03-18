"""Stub implementation of ApiGatewayClientProtocol for bot_service.

Composes StubUserServiceClient and StubBillingServiceClient internally,
so user-related scenarios (register, not-found) work realistically end-to-end.
"""

from typing import Any

from shared.stubs.fixtures import (
    stub_order,
    stub_plan,
    stub_subscription,
    stub_vpn_access,
)
from shared.stubs.user import StubUserServiceClient


class StubApiGatewayClient:
    """Returns realistic data for bot -> api_gateway flows. No HTTP calls."""

    def __init__(self) -> None:
        self._user_client = StubUserServiceClient()

    async def get_me(
        self,
        telegram_id: int,
        username: str | None = None,
        first_name: str | None = None,
    ) -> dict[str, Any]:
        user = await self._user_client.register_or_get(telegram_id, username, first_name)
        sub = stub_subscription(user_id=user["id"])
        return {"user": user, "subscription": sub}

    async def get_plans(self) -> list[dict[str, Any]]:
        return [stub_plan()]

    async def create_order(self, telegram_id: int, plan_id: str) -> dict[str, Any]:
        user = await self._user_client.get_by_telegram_id(telegram_id)
        return stub_order(user_id=user["id"], plan_id=plan_id)

    async def get_order(self, order_id: str) -> dict[str, Any]:
        return stub_order()

    async def get_subscription(self, telegram_id: int) -> dict[str, Any]:
        user = await self._user_client.get_by_telegram_id(telegram_id)
        sub = stub_subscription(user_id=user["id"])
        access = stub_vpn_access(subscription_id=sub["id"])
        return {"subscription": sub, "vpn_access": access}

    async def extend_subscription(self, telegram_id: int, days: int) -> dict[str, Any]:
        user = await self._user_client.get_by_telegram_id(telegram_id)
        return stub_subscription(user_id=user["id"])

    async def close(self) -> None:
        pass
