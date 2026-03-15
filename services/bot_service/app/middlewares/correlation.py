from __future__ import annotations

from typing import Any, Awaitable, Callable
from uuid import uuid4

import structlog
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject


class CorrelationMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        correlation_id = str(uuid4())
        structlog.contextvars.bind_contextvars(correlation_id=correlation_id)
        data["correlation_id"] = correlation_id
        try:
            return await handler(event, data)
        finally:
            structlog.contextvars.unbind_contextvars("correlation_id")
