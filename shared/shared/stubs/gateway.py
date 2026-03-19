"""Stub implementation of ApiGatewayClientProtocol for bot_service.

Composes StubUserServiceClient and StubBillingServiceClient internally,
so user- and billing-related scenarios work realistically end-to-end.
"""

from typing import Any

from shared.exceptions import NotFoundError
from shared.stubs.billing import StubBillingServiceClient
from shared.stubs.fixtures import stub_vpn_access
from shared.stubs.user import StubUserServiceClient


class StubApiGatewayClient:
    """Returns realistic data for bot -> api_gateway flows. No HTTP calls."""

    def __init__(self) -> None:
        self._user_client = StubUserServiceClient()
        self._billing_client = StubBillingServiceClient()

    async def get_me(
        self,
        telegram_id: int,
        username: str | None = None,
        first_name: str | None = None,
    ) -> dict[str, Any]:
        user = await self._user_client.register_or_get(telegram_id, username, first_name)
        subscription = await self._billing_client.get_active_subscription(user["id"])
        return {"user": user, "subscription": subscription}

    async def get_plans(self) -> list[dict[str, Any]]:
        return await self._billing_client.list_plans()

    async def create_order(self, telegram_id: int, plan_id: str) -> dict[str, Any]:
        user = await self._user_client.get_by_telegram_id(telegram_id)
        return await self._billing_client.create_order(user["id"], plan_id)

    async def get_order(self, order_id: str) -> dict[str, Any]:
        return await self._billing_client.get_order(order_id)

    async def get_subscription(self, telegram_id: int) -> dict[str, Any]:
        user = await self._user_client.get_by_telegram_id(telegram_id)
        subscription = await self._billing_client.get_active_subscription(user["id"])

        vpn_access: dict[str, Any] | None = None
        if subscription:
            vpn_access = stub_vpn_access(subscription_id=subscription["id"])

        return {"subscription": subscription, "vpn_access": vpn_access}

    async def extend_subscription(self, telegram_id: int, days: int) -> dict[str, Any]:
        user = await self._user_client.get_by_telegram_id(telegram_id)
        subscription = await self._billing_client.get_active_subscription(user["id"])
        if not subscription:
            raise NotFoundError("No active subscription found")
        return await self._billing_client.extend_subscription(subscription["id"], days)

    async def close(self) -> None:
        pass
