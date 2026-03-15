from typing import Any

from shared.clients.base import BaseHTTPClient


class UserServiceClient(BaseHTTPClient):
    async def register_or_get(self, telegram_id: int, username: str | None = None, first_name: str | None = None) -> dict[str, Any]:
        return await self.post("/users/", json={"telegram_id": telegram_id, "username": username, "first_name": first_name})

    async def get_user(self, user_id: str) -> dict[str, Any]:
        return await self.get(f"/users/{user_id}")

    async def get_by_telegram_id(self, telegram_id: int) -> dict[str, Any]:
        return await self.get(f"/users/by-telegram/{telegram_id}")

    async def list_users(self, offset: int = 0, limit: int = 50) -> dict[str, Any]:
        return await self.get("/users/", params={"offset": offset, "limit": limit})

    async def update_user(self, user_id: str, **kwargs: Any) -> dict[str, Any]:
        return await self.patch(f"/users/{user_id}", json=kwargs)
