from __future__ import annotations

from typing import Any, Awaitable, Callable

import structlog
from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

logger = structlog.get_logger(__name__)

_ERROR_TEXT = "Произошла ошибка. Попробуйте позже."


class ErrorHandlerMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        try:
            return await handler(event, data)
        except Exception:
            logger.exception("unhandled_error")
            try:
                if isinstance(event, Message):
                    await event.answer(_ERROR_TEXT)
                elif isinstance(event, CallbackQuery):
                    await event.answer(_ERROR_TEXT, show_alert=True)
            except Exception:
                logger.exception("failed_to_send_error_message")
            return None
