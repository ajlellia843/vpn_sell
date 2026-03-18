"""Stub implementation of UserServiceClientProtocol.

Supports realistic scenarios:
  - register_or_get: returns existing or "newly created" user
  - get_by_telegram_id: found / not-found (raises NotFoundError)
  - get_user: found / not-found (raises NotFoundError)
  - list_users: returns paginated {items, total}
  - update_user: returns merged user

All responses are structurally identical to UserRead.model_dump(mode='json').
"""

from typing import Any

from shared.exceptions import NotFoundError
from shared.stubs.fixtures import (
    STUB_TELEGRAM_ID,
    STUB_TELEGRAM_ID_UNKNOWN,
    STUB_USER_ID,
    stub_user,
    stub_user_second,
)

# In-memory store seeded with known users; acts as a tiny fake DB.
_DEFAULT_USERS: list[dict] = [stub_user(), stub_user_second()]


class StubUserServiceClient:
    """Returns realistic fixture data for user_service. Raises NotFoundError for unknown users."""

    def __init__(self) -> None:
        self._users: list[dict] = [u.copy() for u in _DEFAULT_USERS]

    # ── helpers ──────────────────────────────────────────────────────

    def _find_by_telegram_id(self, telegram_id: int) -> dict | None:
        return next((u for u in self._users if u["telegram_id"] == telegram_id), None)

    def _find_by_id(self, user_id: str) -> dict | None:
        return next((u for u in self._users if u["id"] == user_id), None)

    # ── protocol methods ─────────────────────────────────────────────

    async def register_or_get(
        self,
        telegram_id: int,
        username: str | None = None,
        first_name: str | None = None,
    ) -> dict[str, Any]:
        existing = self._find_by_telegram_id(telegram_id)
        if existing:
            return existing
        new_user = stub_user(telegram_id=telegram_id, username=username, first_name=first_name)
        import uuid as _uuid
        new_user["id"] = str(_uuid.uuid4())
        self._users.append(new_user)
        return new_user

    async def get_user(self, user_id: str) -> dict[str, Any]:
        user = self._find_by_id(user_id)
        if not user:
            raise NotFoundError(f"User {user_id} not found")
        return user

    async def get_by_telegram_id(self, telegram_id: int) -> dict[str, Any]:
        user = self._find_by_telegram_id(telegram_id)
        if not user:
            raise NotFoundError(f"User with telegram_id={telegram_id} not found")
        return user

    async def list_users(self, offset: int = 0, limit: int = 50) -> dict[str, Any]:
        page = self._users[offset : offset + limit]
        return {"items": page, "total": len(self._users)}

    async def update_user(self, user_id: str, **kwargs: Any) -> dict[str, Any]:
        user = self._find_by_id(user_id)
        if not user:
            raise NotFoundError(f"User {user_id} not found")
        user.update(kwargs)
        return user

    async def close(self) -> None:
        pass
