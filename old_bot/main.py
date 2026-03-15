"""Application entrypoint."""

from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode

from routers.public import public_router
from settings import get_settings

logger = logging.getLogger(__name__)


def setup_logging() -> None:
    """Configure logging for the application."""

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def create_dispatcher() -> Dispatcher:
    """Create and configure dispatcher."""

    dispatcher = Dispatcher()
    dispatcher.include_router(public_router)
    return dispatcher


async def start_bot() -> None:
    """Initialize dependencies and start polling."""

    setup_logging()
    settings = get_settings()
    bot = Bot(
        token=settings.BOT_TOKEN,
        defaults=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dispatcher = create_dispatcher()

    logger.info("Starting application")
    try:
        logger.info("Polling started successfully")
        await dispatcher.start_polling(bot)
    finally:
        await bot.session.close()


def main() -> None:
    """Run application."""

    try:
        asyncio.run(start_bot())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Application shutdown")


if __name__ == "__main__":
    main()
