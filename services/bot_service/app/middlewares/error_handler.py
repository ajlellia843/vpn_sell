from __future__ import annotations

import json
import time
from pathlib import Path
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
        except Exception as e:
            # #region agent log
            try:
                _log_path = Path(__file__).resolve().parent.parent.parent.parent.parent / "debug-56837c.log"
                with open(_log_path, "a", encoding="utf-8") as _f:
                    _f.write(json.dumps({"sessionId": "56837c", "hypothesisId": "E", "location": "error_handler.py:catch", "message": "exception in handler", "data": {"exc_type": type(e).__name__, "exc_msg": str(e)}, "timestamp": int(time.time() * 1000)}) + "\n")
            except Exception:
                pass
            # #endregion
            logger.exception("unhandled_error")
            try:
                if isinstance(event, Message):
                    await event.answer(_ERROR_TEXT)
                elif isinstance(event, CallbackQuery):
                    await event.answer(_ERROR_TEXT, show_alert=True)
            except Exception:
                logger.exception("failed_to_send_error_message")
            return None
