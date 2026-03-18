"""Stub implementation of UserServiceClientProtocol."""

from typing import Any

from shared.stubs.fixtures import stub_user


class StubUserServiceClient:
    """Returns minimal fixture data for user_service. No HTTP calls."""

    async def register_or_get(
        self,
        telegram_id: int,
        username: str | None = None,
        first_name: str | None = None,
    ) -> dict[str, Any]:
        return stub_user(telegram_id=telegram_id, username=username, first_name=first_name)

    async def get_user(self, user_id: str) -> dict[str, Any]:
        return stub_user()

    async def get_by_telegram_id(self, telegram_id: int) -> dict[str, Any]:
        return stub_user(telegram_id=telegram_id)

    async def list_users(self, offset: int = 0, limit: int = 50) -> dict[str, Any]:
        return {"items": [stub_user()], "total": 1}

    async def update_user(self, user_id: str, **kwargs: Any) -> dict[str, Any]:
        u = stub_user()
        u.update(kwargs)
        return u

    async def close(self) -> None:
        pass
