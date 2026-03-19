"""Stub implementation of BillingServiceClientProtocol.

In-memory store seeded with known plans, orders, subscriptions.
Supports realistic scenarios:
  - list_plans (only active)
  - get_plan found / not-found
  - create_order success / plan not found
  - get_order found / not-found
  - get_active_subscription present / absent (returns None)
  - extend_subscription success / not-found
  - revoke_subscription success / not-found
  - list_orders, list_subscriptions with pagination shape {items, total}

All responses are structurally compatible with PlanRead, OrderRead, SubscriptionRead.
"""

from __future__ import annotations

import uuid as _uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from shared.exceptions import NotFoundError
from shared.stubs.fixtures import (
    STUB_ORDER_ID,
    STUB_PLAN_ID,
    STUB_SUBSCRIPTION_ID,
    STUB_USER_ID,
    STUB_USER_ID_NO_SUB,
    stub_order,
    stub_order_paid,
    stub_plan,
    stub_plan_inactive,
    stub_plan_second,
    stub_subscription,
    stub_subscription_expired,
)


class StubBillingServiceClient:
    """Returns realistic fixture data for billing_service. No HTTP calls."""

    def __init__(self) -> None:
        self._plans: list[dict] = [stub_plan(), stub_plan_second(), stub_plan_inactive()]
        self._orders: list[dict] = [stub_order(), stub_order_paid()]
        self._subscriptions: list[dict] = [stub_subscription(), stub_subscription_expired()]

    # ── helpers ──────────────────────────────────────────────────────

    def _find_plan(self, plan_id: str) -> dict | None:
        return next((p for p in self._plans if p["id"] == plan_id), None)

    def _find_order(self, order_id: str) -> dict | None:
        return next((o for o in self._orders if o["id"] == order_id), None)

    def _find_subscription(self, sub_id: str) -> dict | None:
        return next((s for s in self._subscriptions if s["id"] == sub_id), None)

    @staticmethod
    def _paginate(items: list[dict], offset: int, limit: int) -> dict[str, Any]:
        return {"items": items[offset : offset + limit], "total": len(items)}

    # ── plans ────────────────────────────────────────────────────────

    async def list_plans(self) -> list[dict[str, Any]]:
        return [p for p in self._plans if p.get("is_active", True)]

    async def get_plan(self, plan_id: str) -> dict[str, Any]:
        plan = self._find_plan(plan_id)
        if not plan:
            raise NotFoundError("Plan not found")
        return plan

    async def create_plan(self, data: dict[str, Any]) -> dict[str, Any]:
        p = stub_plan(plan_id=str(_uuid.uuid4()))
        p.update(data)
        self._plans.append(p)
        return p

    async def update_plan(self, plan_id: str, data: dict[str, Any]) -> dict[str, Any]:
        plan = self._find_plan(plan_id)
        if not plan:
            raise NotFoundError("Plan not found")
        plan.update(data)
        return plan

    # ── orders ───────────────────────────────────────────────────────

    async def create_order(self, user_id: str, plan_id: str) -> dict[str, Any]:
        plan = self._find_plan(plan_id)
        if not plan or not plan.get("is_active", True):
            raise NotFoundError("Plan not found or inactive")

        new_order = stub_order(
            order_id=str(_uuid.uuid4()),
            user_id=user_id,
            plan_id=plan_id,
            external_payment_id=f"stub-ext-{_uuid.uuid4().hex[:8]}",
        )
        new_order["amount"] = plan["price"]
        self._orders.append(new_order)
        return new_order

    async def get_order(self, order_id: str) -> dict[str, Any]:
        order = self._find_order(order_id)
        if not order:
            raise NotFoundError("Order not found")
        return order

    async def list_orders_by_user(self, user_id: str) -> list[dict[str, Any]]:
        return [o for o in self._orders if o["user_id"] == user_id]

    async def list_orders(
        self,
        offset: int = 0,
        limit: int = 50,
        status: str | None = None,
    ) -> dict[str, Any]:
        filtered = self._orders
        if status:
            filtered = [o for o in filtered if o["status"] == status]
        return self._paginate(filtered, offset, limit)

    # ── subscriptions ────────────────────────────────────────────────

    async def get_active_subscription(self, user_id: str) -> dict[str, Any] | None:
        return next(
            (s for s in self._subscriptions if s["user_id"] == user_id and s["status"] == "active"),
            None,
        )

    async def get_subscription(self, subscription_id: str) -> dict[str, Any]:
        sub = self._find_subscription(subscription_id)
        if not sub:
            raise NotFoundError("Subscription not found")
        return sub

    async def list_subscriptions(
        self,
        offset: int = 0,
        limit: int = 50,
        status: str | None = None,
    ) -> dict[str, Any]:
        filtered = self._subscriptions
        if status:
            filtered = [s for s in filtered if s["status"] == status]
        return self._paginate(filtered, offset, limit)

    async def extend_subscription(self, subscription_id: str, days: int) -> dict[str, Any]:
        sub = self._find_subscription(subscription_id)
        if not sub:
            raise NotFoundError("Subscription not found")
        end_at = datetime.fromisoformat(sub["end_at"])
        sub["end_at"] = (end_at + timedelta(days=days)).isoformat()
        return sub

    async def revoke_subscription(self, subscription_id: str) -> dict[str, Any]:
        sub = self._find_subscription(subscription_id)
        if not sub:
            raise NotFoundError("Subscription not found")
        sub["status"] = "cancelled"
        return sub

    async def close(self) -> None:
        pass
