from typing import Any

from shared.clients.base import BaseHTTPClient


class VPNServiceClient(BaseHTTPClient):
    async def provision(self, subscription_id: str, user_id: str, plan_duration_days: int, traffic_limit_gb: int | None = None, device_limit: int = 1) -> dict[str, Any]:
        return await self.post("/provision", json={
            "subscription_id": subscription_id,
            "user_id": user_id,
            "plan_duration_days": plan_duration_days,
            "traffic_limit_gb": traffic_limit_gb,
            "device_limit": device_limit,
        })

    async def extend(self, subscription_id: str, days: int) -> dict[str, Any]:
        return await self.post("/extend", json={"subscription_id": subscription_id, "days": days})

    async def disable(self, subscription_id: str) -> dict[str, Any]:
        return await self.post("/disable", json={"subscription_id": subscription_id})

    async def enable(self, subscription_id: str) -> dict[str, Any]:
        return await self.post("/enable", json={"subscription_id": subscription_id})

    async def get_access(self, subscription_id: str) -> dict[str, Any]:
        return await self.get(f"/access/{subscription_id}")
