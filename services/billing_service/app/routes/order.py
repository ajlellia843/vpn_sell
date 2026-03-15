import uuid
from collections.abc import Sequence

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from shared.exceptions import NotFoundError
from shared.schemas.order import OrderCreate, OrderRead

from app.dependencies import get_session
from app.repositories.order import OrderRepository
from app.services.billing import BillingService

router = APIRouter(prefix="/orders", tags=["orders"])


def _billing(request: Request, session: AsyncSession) -> BillingService:
    return BillingService(
        session=session,
        yookassa=request.app.state.yookassa,
        vpn_client=request.app.state.vpn_client,
    )


@router.get("/", response_model=list[OrderRead])
async def list_orders(
    offset: int = 0,
    limit: int = 100,
    status: str | None = None,
    session: AsyncSession = Depends(get_session),
) -> Sequence[OrderRead]:
    repo = OrderRepository(session)
    return await repo.get_all_filtered(offset=offset, limit=limit, status=status)


@router.get("/{order_id}", response_model=OrderRead)
async def get_order(
    order_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> OrderRead:
    repo = OrderRepository(session)
    order = await repo.get_by_id(order_id)
    if order is None:
        raise NotFoundError("Order not found")
    return order


@router.get("/user/{user_id}", response_model=list[OrderRead])
async def get_user_orders(
    user_id: uuid.UUID,
    offset: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_session),
) -> Sequence[OrderRead]:
    repo = OrderRepository(session)
    return await repo.get_by_user_id(user_id, offset=offset, limit=limit)


@router.post("/", response_model=OrderRead, status_code=201)
async def create_order(
    data: OrderCreate,
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> OrderRead:
    billing = _billing(request, session)
    return await billing.create_order(user_id=data.user_id, plan_id=data.plan_id)
