"""Smoke tests for the billing stub chain: StubBillingServiceClient + gateway billing flows.

Run with: pytest tests/test_billing_stub_chain.py -v
No external services or DB required.
"""

import pytest

from shared.exceptions import NotFoundError
from shared.schemas.order import OrderRead
from shared.schemas.plan import PlanRead
from shared.schemas.subscription import SubscriptionRead
from shared.stubs.billing import StubBillingServiceClient
from shared.stubs.fixtures import (
    STUB_ORDER_ID,
    STUB_PLAN_ID,
    STUB_PLAN_ID_2,
    STUB_PLAN_ID_INACTIVE,
    STUB_SUBSCRIPTION_ID,
    STUB_SUBSCRIPTION_ID_EXPIRED,
    STUB_TELEGRAM_ID,
    STUB_TELEGRAM_ID_UNKNOWN,
    STUB_USER_ID,
    STUB_USER_ID_NO_SUB,
)
from shared.stubs.gateway import StubApiGatewayClient


# ── StubBillingServiceClient ──────────────────────────────────────────


@pytest.fixture
def billing() -> StubBillingServiceClient:
    return StubBillingServiceClient()


class TestPlans:
    @pytest.mark.asyncio
    async def test_list_plans_returns_only_active(self, billing: StubBillingServiceClient):
        plans = await billing.list_plans()
        assert len(plans) == 2
        for p in plans:
            assert p["is_active"] is True
            PlanRead.model_validate(p)

    @pytest.mark.asyncio
    async def test_get_plan_found(self, billing: StubBillingServiceClient):
        plan = await billing.get_plan(STUB_PLAN_ID)
        assert plan["id"] == STUB_PLAN_ID
        PlanRead.model_validate(plan)

    @pytest.mark.asyncio
    async def test_get_plan_not_found(self, billing: StubBillingServiceClient):
        with pytest.raises(NotFoundError):
            await billing.get_plan("00000000-0000-0000-0000-000000000000")

    @pytest.mark.asyncio
    async def test_get_plan_inactive_still_found_by_id(self, billing: StubBillingServiceClient):
        """Inactive plan is accessible by id (same as real service)."""
        plan = await billing.get_plan(STUB_PLAN_ID_INACTIVE)
        assert plan["is_active"] is False
        PlanRead.model_validate(plan)


class TestOrders:
    @pytest.mark.asyncio
    async def test_create_order_success(self, billing: StubBillingServiceClient):
        order = await billing.create_order(STUB_USER_ID, STUB_PLAN_ID)
        assert order["user_id"] == STUB_USER_ID
        assert order["plan_id"] == STUB_PLAN_ID
        assert order["status"] == "pending"
        assert order["payment_url"] is not None
        OrderRead.model_validate(order)

    @pytest.mark.asyncio
    async def test_create_order_plan_not_found(self, billing: StubBillingServiceClient):
        with pytest.raises(NotFoundError, match="Plan not found"):
            await billing.create_order(STUB_USER_ID, "00000000-0000-0000-0000-000000000000")

    @pytest.mark.asyncio
    async def test_create_order_inactive_plan(self, billing: StubBillingServiceClient):
        with pytest.raises(NotFoundError, match="inactive"):
            await billing.create_order(STUB_USER_ID, STUB_PLAN_ID_INACTIVE)

    @pytest.mark.asyncio
    async def test_get_order_found(self, billing: StubBillingServiceClient):
        order = await billing.get_order(STUB_ORDER_ID)
        assert order["id"] == STUB_ORDER_ID
        OrderRead.model_validate(order)

    @pytest.mark.asyncio
    async def test_get_order_not_found(self, billing: StubBillingServiceClient):
        with pytest.raises(NotFoundError):
            await billing.get_order("00000000-0000-0000-0000-000000000000")

    @pytest.mark.asyncio
    async def test_list_orders_pagination_shape(self, billing: StubBillingServiceClient):
        result = await billing.list_orders(offset=0, limit=10)
        assert "items" in result
        assert "total" in result
        assert isinstance(result["items"], list)
        for o in result["items"]:
            OrderRead.model_validate(o)

    @pytest.mark.asyncio
    async def test_list_orders_filter_by_status(self, billing: StubBillingServiceClient):
        result = await billing.list_orders(status="paid")
        assert all(o["status"] == "paid" for o in result["items"])

    @pytest.mark.asyncio
    async def test_list_orders_by_user(self, billing: StubBillingServiceClient):
        orders = await billing.list_orders_by_user(STUB_USER_ID)
        assert isinstance(orders, list)
        assert all(o["user_id"] == STUB_USER_ID for o in orders)


class TestSubscriptions:
    @pytest.mark.asyncio
    async def test_get_active_subscription_found(self, billing: StubBillingServiceClient):
        sub = await billing.get_active_subscription(STUB_USER_ID)
        assert sub is not None
        assert sub["status"] == "active"
        assert sub["user_id"] == STUB_USER_ID
        SubscriptionRead.model_validate(sub)

    @pytest.mark.asyncio
    async def test_get_active_subscription_absent(self, billing: StubBillingServiceClient):
        sub = await billing.get_active_subscription(STUB_USER_ID_NO_SUB)
        assert sub is None

    @pytest.mark.asyncio
    async def test_get_subscription_by_id(self, billing: StubBillingServiceClient):
        sub = await billing.get_subscription(STUB_SUBSCRIPTION_ID)
        assert sub["id"] == STUB_SUBSCRIPTION_ID
        SubscriptionRead.model_validate(sub)

    @pytest.mark.asyncio
    async def test_get_subscription_not_found(self, billing: StubBillingServiceClient):
        with pytest.raises(NotFoundError):
            await billing.get_subscription("00000000-0000-0000-0000-000000000000")

    @pytest.mark.asyncio
    async def test_extend_subscription_success(self, billing: StubBillingServiceClient):
        original_end = (await billing.get_subscription(STUB_SUBSCRIPTION_ID))["end_at"]
        extended = await billing.extend_subscription(STUB_SUBSCRIPTION_ID, 30)
        assert extended["id"] == STUB_SUBSCRIPTION_ID
        assert extended["end_at"] > original_end
        SubscriptionRead.model_validate(extended)

    @pytest.mark.asyncio
    async def test_extend_subscription_not_found(self, billing: StubBillingServiceClient):
        with pytest.raises(NotFoundError):
            await billing.extend_subscription("00000000-0000-0000-0000-000000000000", 10)

    @pytest.mark.asyncio
    async def test_revoke_subscription_success(self, billing: StubBillingServiceClient):
        revoked = await billing.revoke_subscription(STUB_SUBSCRIPTION_ID)
        assert revoked["status"] == "cancelled"
        SubscriptionRead.model_validate(revoked)

    @pytest.mark.asyncio
    async def test_revoke_subscription_not_found(self, billing: StubBillingServiceClient):
        with pytest.raises(NotFoundError):
            await billing.revoke_subscription("00000000-0000-0000-0000-000000000000")

    @pytest.mark.asyncio
    async def test_list_subscriptions_pagination(self, billing: StubBillingServiceClient):
        result = await billing.list_subscriptions()
        assert "items" in result
        assert "total" in result
        for s in result["items"]:
            SubscriptionRead.model_validate(s)

    @pytest.mark.asyncio
    async def test_list_subscriptions_filter_by_status(self, billing: StubBillingServiceClient):
        result = await billing.list_subscriptions(status="active")
        assert all(s["status"] == "active" for s in result["items"])


# ── StubApiGatewayClient (billing-related flows) ─────────────────────


@pytest.fixture
def gw() -> StubApiGatewayClient:
    return StubApiGatewayClient()


class TestGatewayBillingFlows:
    @pytest.mark.asyncio
    async def test_get_me_includes_subscription(self, gw: StubApiGatewayClient):
        result = await gw.get_me(STUB_TELEGRAM_ID, "stub_user", "Stub")
        assert "subscription" in result
        sub = result["subscription"]
        if sub is not None:
            SubscriptionRead.model_validate(sub)

    @pytest.mark.asyncio
    async def test_get_plans_returns_active_only(self, gw: StubApiGatewayClient):
        plans = await gw.get_plans()
        assert len(plans) >= 1
        for p in plans:
            assert p["is_active"] is True
            PlanRead.model_validate(p)

    @pytest.mark.asyncio
    async def test_create_order_through_gateway(self, gw: StubApiGatewayClient):
        order = await gw.create_order(STUB_TELEGRAM_ID, STUB_PLAN_ID)
        assert order["status"] == "pending"
        OrderRead.model_validate(order)

    @pytest.mark.asyncio
    async def test_create_order_unknown_user(self, gw: StubApiGatewayClient):
        with pytest.raises(NotFoundError):
            await gw.create_order(STUB_TELEGRAM_ID_UNKNOWN, STUB_PLAN_ID)

    @pytest.mark.asyncio
    async def test_create_order_bad_plan(self, gw: StubApiGatewayClient):
        with pytest.raises(NotFoundError):
            await gw.create_order(STUB_TELEGRAM_ID, "00000000-0000-0000-0000-000000000000")

    @pytest.mark.asyncio
    async def test_get_order_through_gateway(self, gw: StubApiGatewayClient):
        order = await gw.get_order(STUB_ORDER_ID)
        OrderRead.model_validate(order)

    @pytest.mark.asyncio
    async def test_get_subscription_with_vpn(self, gw: StubApiGatewayClient):
        result = await gw.get_subscription(STUB_TELEGRAM_ID)
        assert "subscription" in result
        assert "vpn_access" in result

    @pytest.mark.asyncio
    async def test_extend_subscription_through_gateway(self, gw: StubApiGatewayClient):
        result = await gw.extend_subscription(STUB_TELEGRAM_ID, 15)
        SubscriptionRead.model_validate(result)

    @pytest.mark.asyncio
    async def test_extend_subscription_unknown_user(self, gw: StubApiGatewayClient):
        with pytest.raises(NotFoundError):
            await gw.extend_subscription(STUB_TELEGRAM_ID_UNKNOWN, 15)
