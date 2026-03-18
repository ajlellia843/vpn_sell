"""Shared stub fixture data for stub implementations.

All user-related fixtures produce dicts compatible with shared.schemas.user.UserRead
so that stub responses are structurally identical to real service responses.
"""

import uuid
from datetime import datetime, timezone
from decimal import Decimal

STUB_USER_ID = "a0000000-0000-0000-0000-000000000001"
STUB_USER_ID_2 = "a0000000-0000-0000-0000-000000000002"
STUB_PLAN_ID = "b0000000-0000-0000-0000-000000000001"
STUB_ORDER_ID = "c0000000-0000-0000-0000-000000000001"
STUB_SUBSCRIPTION_ID = "d0000000-0000-0000-0000-000000000001"

# Known telegram IDs for stub scenarios
STUB_TELEGRAM_ID = 12345
STUB_TELEGRAM_ID_UNKNOWN = 99999999

_NOW = datetime.now(timezone.utc)
NOW = _NOW.isoformat()


def _user_dict(
    *,
    user_id: str = STUB_USER_ID,
    telegram_id: int = STUB_TELEGRAM_ID,
    username: str | None = "stub_user",
    first_name: str | None = "Stub",
    is_active: bool = True,
) -> dict:
    """Return dict matching UserRead.model_dump(mode='json') output."""
    return {
        "id": user_id,
        "telegram_id": telegram_id,
        "username": username,
        "first_name": first_name,
        "is_active": is_active,
        "created_at": NOW,
        "updated_at": NOW,
    }


# ── user fixtures ────────────────────────────────────────────────────

def stub_user(
    telegram_id: int = STUB_TELEGRAM_ID,
    username: str | None = "stub_user",
    first_name: str | None = "Stub",
) -> dict:
    return _user_dict(telegram_id=telegram_id, username=username, first_name=first_name)


def stub_user_second() -> dict:
    """A second known user for list scenarios."""
    return _user_dict(
        user_id=STUB_USER_ID_2,
        telegram_id=67890,
        username="second_user",
        first_name="Second",
    )


# ── plan / order / subscription / vpn fixtures ───────────────────────

def stub_plan() -> dict:
    return {
        "id": STUB_PLAN_ID,
        "name": "Stub Plan",
        "duration_days": 30,
        "price": "100",
        "currency": "RUB",
        "description": None,
        "traffic_limit_gb": None,
        "device_limit": 1,
        "is_active": True,
        "created_at": NOW,
    }


def stub_order(user_id: str = STUB_USER_ID, plan_id: str = STUB_PLAN_ID) -> dict:
    return {
        "id": STUB_ORDER_ID,
        "user_id": user_id,
        "plan_id": plan_id,
        "status": "pending",
        "amount": "100",
        "currency": "RUB",
        "payment_url": "https://stub.example/pay",
        "external_payment_id": str(uuid.uuid4()),
        "provider_payload": {},
        "created_at": NOW,
        "updated_at": NOW,
    }


def stub_subscription(
    user_id: str = STUB_USER_ID,
    plan_id: str = STUB_PLAN_ID,
    order_id: str = STUB_ORDER_ID,
) -> dict:
    return {
        "id": STUB_SUBSCRIPTION_ID,
        "user_id": user_id,
        "plan_id": plan_id,
        "order_id": order_id,
        "start_at": NOW,
        "end_at": NOW,
        "status": "active",
        "auto_provisioned": False,
        "created_at": NOW,
    }


def stub_vpn_access(subscription_id: str = STUB_SUBSCRIPTION_ID) -> dict:
    return {
        "id": str(uuid.uuid4()),
        "subscription_id": subscription_id,
        "xui_client_id": "stub-client-id",
        "inbound_id": 1,
        "connection_uri": "vless://stub@stub.example:443",
        "provision_status": "provisioned",
        "created_at": NOW,
        "updated_at": NOW,
    }
