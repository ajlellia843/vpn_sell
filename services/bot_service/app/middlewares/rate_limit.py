from __future__ import annotations

import time
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

_MAX_REQUESTS = 30
_WINDOW_SECONDS = 60.0
_RATE_LIMITED_TEXT = "Слишком много запросов. Подождите немного."


class RateLimitMiddleware(BaseMiddleware):
    def __init__(self) -> None:
        super().__init__()
        self._timestamps: dict[int, list[float]] = {}

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user_id = self._extract_user_id(event)
        if user_id is None:
            return await handler(event, data)

        now = time.monotonic()
        window = self._timestamps.setdefault(user_id, [])
        window[:] = [ts for ts in window if now - ts < _WINDOW_SECONDS]

        if len(window) >= _MAX_REQUESTS:
            return await self._reject(event)

        window.append(now)
        return await handler(event, data)

    @staticmethod
    def _extract_user_id(event: TelegramObject) -> int | None:
        if isinstance(event, (Message, CallbackQuery)) and event.from_user:
            return event.from_user.id
        return None

    @staticmethod
    async def _reject(event: TelegramObject) -> None:
        if isinstance(event, Message):
            await event.answer(_RATE_LIMITED_TEXT)
        elif isinstance(event, CallbackQuery):
            await event.answer(_RATE_LIMITED_TEXT, show_alert=True)
