"""Shared stub fixture data for stub implementations.

All fixtures produce dicts structurally identical to corresponding Pydantic schema
model_dump(mode='json') output (UserRead, PlanRead, OrderRead, SubscriptionRead, VPNAccessRead).
Stable deterministic IDs ensure reproducible stub responses.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

STUB_USER_ID = "a0000000-0000-0000-0000-000000000001"
STUB_USER_ID_2 = "a0000000-0000-0000-0000-000000000002"
STUB_USER_ID_NO_SUB = "a0000000-0000-0000-0000-000000000099"

STUB_PLAN_ID = "b0000000-0000-0000-0000-000000000001"
STUB_PLAN_ID_2 = "b0000000-0000-0000-0000-000000000002"
STUB_PLAN_ID_INACTIVE = "b0000000-0000-0000-0000-000000000099"

STUB_ORDER_ID = "c0000000-0000-0000-0000-000000000001"
STUB_ORDER_ID_PAID = "c0000000-0000-0000-0000-000000000002"

STUB_SUBSCRIPTION_ID = "d0000000-0000-0000-0000-000000000001"
STUB_SUBSCRIPTION_ID_EXPIRED = "d0000000-0000-0000-0000-000000000099"

STUB_TELEGRAM_ID = 12345
STUB_TELEGRAM_ID_UNKNOWN = 99999999

_NOW = datetime.now(timezone.utc)
NOW = _NOW.isoformat()
_30D = (_NOW + timedelta(days=30)).isoformat()
_PAST = (_NOW - timedelta(days=5)).isoformat()


# ── user fixtures ────────────────────────────────────────────────────

def _user_dict(
    *,
    user_id: str = STUB_USER_ID,
    telegram_id: int = STUB_TELEGRAM_ID,
    username: str | None = "stub_user",
    first_name: str | None = "Stub",
    is_active: bool = True,
) -> dict:
    return {
        "id": user_id,
        "telegram_id": telegram_id,
        "username": username,
        "first_name": first_name,
        "is_active": is_active,
        "created_at": NOW,
        "updated_at": NOW,
    }


def stub_user(
    telegram_id: int = STUB_TELEGRAM_ID,
    username: str | None = "stub_user",
    first_name: str | None = "Stub",
) -> dict:
    return _user_dict(telegram_id=telegram_id, username=username, first_name=first_name)


def stub_user_second() -> dict:
    return _user_dict(
        user_id=STUB_USER_ID_2,
        telegram_id=67890,
        username="second_user",
        first_name="Second",
    )


# ── plan fixtures ────────────────────────────────────────────────────

def stub_plan(
    plan_id: str = STUB_PLAN_ID,
    name: str = "Stub Plan 30d",
    duration_days: int = 30,
    price: str = "100",
    is_active: bool = True,
) -> dict:
    return {
        "id": plan_id,
        "name": name,
        "duration_days": duration_days,
        "price": price,
        "currency": "RUB",
        "description": None,
        "traffic_limit_gb": None,
        "device_limit": 1,
        "is_active": is_active,
        "created_at": NOW,
    }


def stub_plan_second() -> dict:
    return stub_plan(
        plan_id=STUB_PLAN_ID_2,
        name="Stub Plan 90d",
        duration_days=90,
        price="250",
    )


def stub_plan_inactive() -> dict:
    return stub_plan(
        plan_id=STUB_PLAN_ID_INACTIVE,
        name="Old Plan",
        is_active=False,
    )


# ── order fixtures ───────────────────────────────────────────────────

def stub_order(
    order_id: str = STUB_ORDER_ID,
    user_id: str = STUB_USER_ID,
    plan_id: str = STUB_PLAN_ID,
    status: str = "pending",
    payment_url: str | None = "https://stub.example/pay",
    external_payment_id: str = "stub-ext-pay-001",
) -> dict:
    return {
        "id": order_id,
        "user_id": user_id,
        "plan_id": plan_id,
        "status": status,
        "amount": "100",
        "currency": "RUB",
        "payment_url": payment_url,
        "external_payment_id": external_payment_id,
        "provider_payload": {},
        "created_at": NOW,
        "updated_at": NOW,
    }


def stub_order_paid(user_id: str = STUB_USER_ID) -> dict:
    return stub_order(
        order_id=STUB_ORDER_ID_PAID,
        user_id=user_id,
        status="paid",
        payment_url=None,
        external_payment_id="stub-ext-pay-002",
    )


# ── subscription fixtures ────────────────────────────────────────────

def stub_subscription(
    subscription_id: str = STUB_SUBSCRIPTION_ID,
    user_id: str = STUB_USER_ID,
    plan_id: str = STUB_PLAN_ID,
    order_id: str = STUB_ORDER_ID,
    status: str = "active",
    end_at: str = _30D,
) -> dict:
    return {
        "id": subscription_id,
        "user_id": user_id,
        "plan_id": plan_id,
        "order_id": order_id,
        "start_at": NOW,
        "end_at": end_at,
        "status": status,
        "auto_provisioned": True,
        "created_at": NOW,
    }


def stub_subscription_expired() -> dict:
    return stub_subscription(
        subscription_id=STUB_SUBSCRIPTION_ID_EXPIRED,
        status="expired",
        end_at=_PAST,
    )


# ── vpn fixtures ─────────────────────────────────────────────────────

def stub_vpn_access(subscription_id: str = STUB_SUBSCRIPTION_ID) -> dict:
    return {
        "id": "e0000000-0000-0000-0000-000000000001",
        "subscription_id": subscription_id,
        "xui_client_id": "stub-client-id",
        "inbound_id": 1,
        "connection_uri": "vless://stub@stub.example:443",
        "provision_status": "provisioned",
        "created_at": NOW,
        "updated_at": NOW,
    }
