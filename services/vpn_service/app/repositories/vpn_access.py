import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shared.repository import BaseRepository

from app.models.vpn_access import VPNAccessBinding


class VPNAccessRepository(BaseRepository[VPNAccessBinding]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(VPNAccessBinding, session)

    async def get_by_subscription_id(
        self, subscription_id: uuid.UUID,
    ) -> VPNAccessBinding | None:
        stmt = select(VPNAccessBinding).where(
            VPNAccessBinding.subscription_id == subscription_id,
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
