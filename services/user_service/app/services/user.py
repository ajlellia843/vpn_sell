import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from shared.exceptions import NotFoundError

from app.models.user import User
from app.repositories.user import UserRepository


class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._repo = UserRepository(session)

    async def register_or_get(
        self,
        telegram_id: int,
        username: str | None = None,
        first_name: str | None = None,
    ) -> User:
        existing = await self._repo.get_by_telegram_id(telegram_id)
        if existing:
            return existing
        user = await self._repo.create(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
        )
        await self._session.commit()
        return user

    async def get_by_id(self, user_id: uuid.UUID) -> User:
        user = await self._repo.get_by_id(user_id)
        if not user:
            raise NotFoundError(f"User {user_id} not found")
        return user

    async def get_by_telegram_id(self, telegram_id: int) -> User:
        user = await self._repo.get_by_telegram_id(telegram_id)
        if not user:
            raise NotFoundError(
                f"User with telegram_id={telegram_id} not found",
            )
        return user

    async def list_users(
        self, offset: int = 0, limit: int = 100,
    ) -> tuple[list[User], int]:
        users = await self._repo.get_all(offset=offset, limit=limit)
        total = await self._repo.count()
        return list(users), total

    async def update_user(self, user_id: uuid.UUID, **kwargs: Any) -> User:
        user = await self._repo.update(user_id, **kwargs)
        if not user:
            raise NotFoundError(f"User {user_id} not found")
        await self._session.commit()
        return user
