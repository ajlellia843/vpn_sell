# Shared stub fixture data (UUIDs, minimal shapes) for stub implementations.
# Stubs may override or extend these per service.

import uuid
from datetime import datetime, timezone

# Stable fake IDs for predictable stub responses
STUB_USER_ID = "a0000000-0000-0000-0000-000000000001"
STUB_PLAN_ID = "b0000000-0000-0000-0000-000000000001"
STUB_ORDER_ID = "c0000000-0000-0000-0000-000000000001"
STUB_SUBSCRIPTION_ID = "d0000000-0000-0000-0000-000000000001"

NOW = datetime.now(timezone.utc).isoformat()


def stub_user(
    telegram_id: int = 12345,
    username: str | None = "stub_user",
    first_name: str | None = "Stub",
) -> dict:
    return {
        "id": STUB_USER_ID,
        "telegram_id": telegram_id,
        "username": username,
        "first_name": first_name or "Stub",
        "is_active": True,
        "created_at": NOW,
        "updated_at": NOW,
    }


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
