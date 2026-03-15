import uuid
from collections.abc import Sequence

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from shared.exceptions import NotFoundError
from shared.schemas.subscription import SubscriptionRead

from app.dependencies import get_session
from app.repositories.subscription import SubscriptionRepository
from app.services.billing import BillingService

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


class _ExtendBody(BaseModel):
    days: int


def _billing(request: Request, session: AsyncSession) -> BillingService:
    return BillingService(
        session=session,
        yookassa=request.app.state.yookassa,
        vpn_client=request.app.state.vpn_client,
    )


@router.get("/", response_model=list[SubscriptionRead])
async def list_subscriptions(
    offset: int = 0,
    limit: int = 100,
    status: str | None = None,
    user_id: uuid.UUID | None = None,
    session: AsyncSession = Depends(get_session),
) -> Sequence[SubscriptionRead]:
    repo = SubscriptionRepository(session)
    return await repo.get_all_filtered(
        offset=offset, limit=limit, status=status, user_id=user_id
    )


@router.get("/{sub_id}", response_model=SubscriptionRead)
async def get_subscription(
    sub_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> SubscriptionRead:
    repo = SubscriptionRepository(session)
    sub = await repo.get_by_id(sub_id)
    if sub is None:
        raise NotFoundError("Subscription not found")
    return sub


@router.get("/user/{user_id}/active", response_model=SubscriptionRead | None)
async def get_active_subscription(
    user_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> SubscriptionRead | None:
    repo = SubscriptionRepository(session)
    return await repo.get_active_by_user(user_id)


@router.post("/{sub_id}/extend", response_model=SubscriptionRead)
async def extend_subscription(
    sub_id: uuid.UUID,
    body: _ExtendBody,
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> SubscriptionRead:
    billing = _billing(request, session)
    return await billing.extend_subscription(sub_id, body.days)


@router.post("/{sub_id}/revoke", response_model=SubscriptionRead)
async def revoke_subscription(
    sub_id: uuid.UUID,
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> SubscriptionRead:
    billing = _billing(request, session)
    return await billing.revoke_subscription(sub_id)
