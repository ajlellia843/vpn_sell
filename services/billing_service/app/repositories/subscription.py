import uuid
from collections.abc import Sequence
from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shared.repository import BaseRepository

from app.models.subscription import Subscription


class SubscriptionRepository(BaseRepository[Subscription]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Subscription, session)

    async def get_active_by_user(self, user_id: uuid.UUID) -> Subscription | None:
        stmt = select(Subscription).where(
            Subscription.user_id == user_id,
            Subscription.status == "active",
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def extend_subscription(
        self, sub_id: uuid.UUID, days: int
    ) -> Subscription | None:
        sub = await self.get_by_id(sub_id)
        if sub is None:
            return None
        sub.end_at = sub.end_at + timedelta(days=days)
        await self._session.flush()
        await self._session.refresh(sub)
        return sub

    async def get_all_filtered(
        self,
        offset: int = 0,
        limit: int = 100,
        status: str | None = None,
        user_id: uuid.UUID | None = None,
    ) -> Sequence[Subscription]:
        stmt = select(Subscription).order_by(Subscription.created_at.desc())
        if status:
            stmt = stmt.where(Subscription.status == status)
        if user_id:
            stmt = stmt.where(Subscription.user_id == user_id)
        stmt = stmt.offset(offset).limit(limit)
        result = await self._session.execute(stmt)
        return result.scalars().all()
