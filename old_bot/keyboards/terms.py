"""Keyboards for the user agreement flow."""

from __future__ import annotations

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


class TermsCallback(CallbackData, prefix="terms"):
    """Callback data for user agreement actions."""

    action: str


def terms_accept_kb() -> InlineKeyboardMarkup:
    """Build a keyboard with the accept terms button."""

    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Принять", callback_data=TermsCallback(action="accept"))
    return builder.as_markup()


def terms_back_to_menu_kb() -> InlineKeyboardMarkup:
    """Build a keyboard with the back-to-menu button."""

    builder = InlineKeyboardBuilder()
    builder.button(
        text="⤴️ Вернуться в меню", callback_data=TermsCallback(action="back")
    )
    return builder.as_markup()
