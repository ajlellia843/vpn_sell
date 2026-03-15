from __future__ import annotations

import asyncio
import json
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator

import structlog
import uvicorn
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Update
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from app.config import BotSettings
from app.handlers import (
    instructions,
    payments,
    plans,
    referral,
    start,
    subscription,
    support,
    terms,
)
from app.middlewares.correlation import CorrelationMiddleware
from app.middlewares.error_handler import ErrorHandlerMiddleware
from app.middlewares.logging import LoggingMiddleware
from app.middlewares.rate_limit import RateLimitMiddleware
from app.services.api_client import APIClient

try:
    from shared.logging import setup_logging
except ImportError:
    setup_logging = None  # type: ignore[assignment]

logger = structlog.get_logger(__name__)

settings = BotSettings()  # type: ignore[call-arg]

bot = Bot(
    token=settings.bot_token,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)
dp = Dispatcher(storage=MemoryStorage())

dp.message.outer_middleware(CorrelationMiddleware())
dp.message.outer_middleware(LoggingMiddleware())
dp.message.outer_middleware(RateLimitMiddleware())
dp.message.outer_middleware(ErrorHandlerMiddleware())

dp.callback_query.outer_middleware(CorrelationMiddleware())
dp.callback_query.outer_middleware(LoggingMiddleware())
dp.callback_query.outer_middleware(RateLimitMiddleware())
dp.callback_query.outer_middleware(ErrorHandlerMiddleware())

dp.include_router(start.router)
dp.include_router(plans.router)
dp.include_router(payments.router)
dp.include_router(subscription.router)
dp.include_router(support.router)
dp.include_router(terms.router)
dp.include_router(referral.router)
dp.include_router(instructions.router)

api_client = APIClient(
    base_url=settings.api_gateway_url,
    api_key=settings.service_api_key,
)
bot["api_client"] = api_client


@asynccontextmanager
async def _lifespan(_app: FastAPI) -> AsyncIterator[None]:
    wh_url = f"{settings.webhook_url}/webhook/bot"
    await bot.set_webhook(wh_url)
    logger.info("webhook_set", url=wh_url)
    yield
    await bot.delete_webhook()
    await api_client.close()


def _create_webapp() -> FastAPI:
    app = FastAPI(lifespan=_lifespan)

    @app.post("/webhook/bot")
    async def webhook_handler(update: dict) -> JSONResponse:
        # #region agent log
        try:
            _log_path = Path(__file__).resolve().parent.parent.parent.parent / "debug-56837c.log"
            with open(_log_path, "a", encoding="utf-8") as _f:
                _f.write(json.dumps({"sessionId": "56837c", "hypothesisId": "A", "location": "main.py:webhook_entry", "message": "webhook received", "data": {"update_keys": list(update.keys()), "has_message": "message" in update}, "timestamp": int(time.time() * 1000)}) + "\n")
        except Exception:
            pass
        # #endregion
        telegram_update = Update.model_validate(update, context={"bot": bot})
        await dp.feed_update(bot=bot, update=telegram_update)
        # #region agent log
        try:
            _log_path = Path(__file__).resolve().parent.parent.parent.parent / "debug-56837c.log"
            with open(_log_path, "a", encoding="utf-8") as _f:
                _f.write(json.dumps({"sessionId": "56837c", "hypothesisId": "A", "location": "main.py:webhook_after_feed", "message": "feed_update done", "data": {}, "timestamp": int(time.time() * 1000)}) + "\n")
        except Exception:
            pass
        # #endregion
        return JSONResponse({"ok": True})

    @app.get("/health")
    async def health() -> dict:
        return {"status": "ok", "service": settings.service_name}

    @app.get("/metrics")
    async def metrics() -> bytes:
        from starlette.responses import Response

        return Response(
            content=generate_latest(),
            media_type=CONTENT_TYPE_LATEST,
        )

    return app


async def _run_polling() -> None:
    logger.info("starting_polling")
    try:
        await dp.start_polling(bot)
    finally:
        await api_client.close()


def main() -> None:
    if setup_logging is not None:
        setup_logging(
            service_name=settings.service_name,
            log_level=settings.log_level,
        )

    if settings.bot_mode == "webhook":
        app = _create_webapp()
        uvicorn.run(
            app,
            host=settings.host,
            port=settings.port,
            log_level=settings.log_level.lower(),
        )
    else:
        asyncio.run(_run_polling())


if __name__ == "__main__":
    main()
