from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shared.repository import BaseRepository

from app.models.plan import Plan


class PlanRepository(BaseRepository[Plan]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Plan, session)

    async def get_active_plans(self) -> list[Plan]:
        stmt = select(Plan).where(Plan.is_active.is_(True))
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
