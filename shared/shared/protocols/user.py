"""Protocol for user_service HTTP client. Real: UserServiceClient; stub: StubUserServiceClient."""

from typing import Any, Protocol


class UserServiceClientProtocol(Protocol):
    """Interface for user_service client (register, get, list, update)."""

    async def register_or_get(
        self,
        telegram_id: int,
        username: str | None = None,
        first_name: str | None = None,
    ) -> dict[str, Any]: ...

    async def get_user(self, user_id: str) -> dict[str, Any]: ...

    async def get_by_telegram_id(self, telegram_id: int) -> dict[str, Any]: ...

    async def list_users(
        self,
        offset: int = 0,
        limit: int = 50,
    ) -> dict[str, Any]: ...

    async def update_user(self, user_id: str, **kwargs: Any) -> dict[str, Any]: ...

    async def close(self) -> None: ...
