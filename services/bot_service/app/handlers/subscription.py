"""Handlers for viewing active subscription and VPN access."""

from __future__ import annotations

import structlog
from aiogram import F, Router
from aiogram.types import CallbackQuery

from app.keyboards.common import menu_keyboard
from app.services.api_client import APIClient, APIError
from app.utils.callbacks import CommonMenuCallback
from app.utils.formatting import format_subscription

logger = structlog.get_logger(__name__)

router = Router(name="subscription")


def _api(bot) -> APIClient:  # noqa: ANN001
    return bot["api_client"]


@router.callback_query(CommonMenuCallback.filter(F.action == "my_sub"))
async def show_subscription(callback_query: CallbackQuery) -> None:
    telegram_id = callback_query.from_user.id if callback_query.from_user else 0
    try:
        data = await _api(callback_query.bot).get_subscription(telegram_id)
        sub = data.get("subscription")
        vpn = data.get("vpn_access")
    except APIError:
        sub = None
        vpn = None

    if sub:
        text = format_subscription(sub, vpn)
    else:
        text = "У вас пока нет активной подписки."

    if callback_query.message:
        await callback_query.message.edit_text(
            text,
            reply_markup=menu_keyboard(),
            parse_mode="HTML",
        )
    await callback_query.answer()
