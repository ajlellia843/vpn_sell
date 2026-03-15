import uuid
from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from shared.schemas.user import UserCreate, UserRead, UserUpdate

from app.services.user import UserService


async def _get_session() -> AsyncGenerator[AsyncSession, None]:
    from app.main import db  # deferred to avoid circular import

    async for session in db.get_session():
        yield session


Session = Annotated[AsyncSession, Depends(_get_session)]

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserRead)
async def register_or_get(body: UserCreate, session: Session) -> UserRead:
    svc = UserService(session)
    user = await svc.register_or_get(
        body.telegram_id, body.username, body.first_name,
    )
    return UserRead.model_validate(user)


@router.get("/")
async def list_users(
    session: Session,
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
) -> dict:
    svc = UserService(session)
    users, total = await svc.list_users(offset=offset, limit=limit)
    return {
        "items": [UserRead.model_validate(u) for u in users],
        "total": total,
    }


@router.get("/by-telegram/{telegram_id}", response_model=UserRead)
async def get_by_telegram_id(
    telegram_id: int, session: Session,
) -> UserRead:
    svc = UserService(session)
    user = await svc.get_by_telegram_id(telegram_id)
    return UserRead.model_validate(user)


@router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: uuid.UUID, session: Session) -> UserRead:
    svc = UserService(session)
    user = await svc.get_by_id(user_id)
    return UserRead.model_validate(user)


@router.patch("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: uuid.UUID, body: UserUpdate, session: Session,
) -> UserRead:
    svc = UserService(session)
    data = body.model_dump(exclude_unset=True)
    user = await svc.update_user(user_id, **data)
    return UserRead.model_validate(user)
