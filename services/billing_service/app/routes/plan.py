import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from shared.exceptions import NotFoundError
from shared.schemas.plan import PlanCreate, PlanRead, PlanUpdate

from app.dependencies import get_session
from app.repositories.plan import PlanRepository

router = APIRouter(prefix="/plans", tags=["plans"])


@router.get("/", response_model=list[PlanRead])
async def list_plans(
    session: AsyncSession = Depends(get_session),
) -> list[PlanRead]:
    repo = PlanRepository(session)
    return await repo.get_active_plans()


@router.get("/{plan_id}", response_model=PlanRead)
async def get_plan(
    plan_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> PlanRead:
    repo = PlanRepository(session)
    plan = await repo.get_by_id(plan_id)
    if plan is None:
        raise NotFoundError("Plan not found")
    return plan


@router.post("/", response_model=PlanRead, status_code=201)
async def create_plan(
    data: PlanCreate,
    session: AsyncSession = Depends(get_session),
) -> PlanRead:
    repo = PlanRepository(session)
    plan = await repo.create(**data.model_dump())
    await session.commit()
    return plan


@router.put("/{plan_id}", response_model=PlanRead)
async def update_plan(
    plan_id: uuid.UUID,
    data: PlanUpdate,
    session: AsyncSession = Depends(get_session),
) -> PlanRead:
    repo = PlanRepository(session)
    plan = await repo.update(plan_id, **data.model_dump(exclude_unset=True))
    if plan is None:
        raise NotFoundError("Plan not found")
    await session.commit()
    return plan
