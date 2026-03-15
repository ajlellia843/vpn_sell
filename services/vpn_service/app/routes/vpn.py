import uuid
from collections.abc import AsyncGenerator

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from shared.schemas.vpn_access import (
    ProvisionRequest,
    ProvisionResponse,
    VPNAccessRead,
)

from app.services.provisioning import ProvisioningService

router = APIRouter(prefix="/vpn", tags=["vpn"])


async def _get_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    async with request.app.state.db.session_factory() as session:
        yield session


def _build_service(session: AsyncSession, request: Request) -> ProvisioningService:
    return ProvisioningService(session, request.app.state.vpn_adapter)


class ExtendRequest(BaseModel):
    subscription_id: uuid.UUID
    days: int


class SubscriptionRequest(BaseModel):
    subscription_id: uuid.UUID


@router.post("/provision", response_model=ProvisionResponse)
async def provision(
    body: ProvisionRequest,
    request: Request,
    session: AsyncSession = Depends(_get_session),
) -> ProvisionResponse:
    svc = _build_service(session, request)
    return await svc.provision(body)


@router.post("/extend", response_model=ProvisionResponse)
async def extend(
    body: ExtendRequest,
    request: Request,
    session: AsyncSession = Depends(_get_session),
) -> ProvisionResponse:
    svc = _build_service(session, request)
    return await svc.extend(body.subscription_id, body.days)


@router.post("/disable", status_code=204)
async def disable(
    body: SubscriptionRequest,
    request: Request,
    session: AsyncSession = Depends(_get_session),
) -> None:
    svc = _build_service(session, request)
    await svc.disable(body.subscription_id)


@router.post("/enable", status_code=204)
async def enable(
    body: SubscriptionRequest,
    request: Request,
    session: AsyncSession = Depends(_get_session),
) -> None:
    svc = _build_service(session, request)
    await svc.enable(body.subscription_id)


@router.get("/access/{subscription_id}", response_model=VPNAccessRead)
async def get_access(
    subscription_id: uuid.UUID,
    request: Request,
    session: AsyncSession = Depends(_get_session),
) -> VPNAccessRead:
    svc = _build_service(session, request)
    binding = await svc.get_access(subscription_id)
    return VPNAccessRead.model_validate(binding)
