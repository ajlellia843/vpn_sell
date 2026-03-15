from typing import Any

from fastapi import APIRouter, Query, Request
from pydantic import BaseModel

from shared.clients.billing import BillingServiceClient
from shared.clients.user import UserServiceClient
from shared.clients.vpn import VPNServiceClient
from shared.exceptions import NotFoundError

router = APIRouter(prefix="/bot", tags=["bot"])


def _user_client(request: Request) -> UserServiceClient:
    return request.app.state.user_client


def _billing_client(request: Request) -> BillingServiceClient:
    return request.app.state.billing_client


def _vpn_client(request: Request) -> VPNServiceClient:
    return request.app.state.vpn_client


class RegisterBody(BaseModel):
    telegram_id: int
    username: str | None = None
    first_name: str | None = None


class CreateOrderBody(BaseModel):
    telegram_id: int
    plan_id: str


class ExtendSubscriptionBody(BaseModel):
    telegram_id: int
    days: int


@router.post("/me")
async def register_me(request: Request, body: RegisterBody) -> dict[str, Any]:
    user = await _user_client(request).register_or_get(
        body.telegram_id, body.username, body.first_name,
    )
    subscription = await _billing_client(request).get_active_subscription(user["id"])
    return {"user": user, "subscription": subscription}


@router.get("/me")
async def get_me(
    request: Request,
    telegram_id: int = Query(...),
) -> dict[str, Any]:
    user = await _user_client(request).get_by_telegram_id(telegram_id)
    subscription = await _billing_client(request).get_active_subscription(user["id"])
    return {"user": user, "subscription": subscription}


@router.get("/plans")
async def list_plans(request: Request) -> list[dict[str, Any]]:
    return await _billing_client(request).list_plans()


@router.post("/orders")
async def create_order(request: Request, body: CreateOrderBody) -> dict[str, Any]:
    user = await _user_client(request).get_by_telegram_id(body.telegram_id)
    return await _billing_client(request).create_order(user["id"], body.plan_id)


@router.get("/orders/{order_id}")
async def get_order(request: Request, order_id: str) -> dict[str, Any]:
    return await _billing_client(request).get_order(order_id)


@router.get("/subscription")
async def get_subscription(
    request: Request,
    telegram_id: int = Query(...),
) -> dict[str, Any]:
    user = await _user_client(request).get_by_telegram_id(telegram_id)
    subscription = await _billing_client(request).get_active_subscription(user["id"])

    vpn_access: dict[str, Any] | None = None
    if subscription:
        try:
            vpn_access = await _vpn_client(request).get_access(subscription["id"])
        except NotFoundError:
            vpn_access = None

    return {"subscription": subscription, "vpn_access": vpn_access}


@router.post("/subscription/extend")
async def extend_subscription(
    request: Request,
    body: ExtendSubscriptionBody,
) -> dict[str, Any]:
    user = await _user_client(request).get_by_telegram_id(body.telegram_id)
    subscription = await _billing_client(request).get_active_subscription(user["id"])
    if not subscription:
        raise NotFoundError("No active subscription found")
    return await _billing_client(request).extend_subscription(subscription["id"], body.days)
