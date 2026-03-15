"""Inline keyboards for referral and partner programs."""

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.utils.callbacks import CommonMenuCallback, ReferralActionCallback


def referral_program_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="🚀 Поделиться с друзьями",
        callback_data=ReferralActionCallback(action="share"),
    )
    builder.button(
        text="⤴️ Вернуться в меню", callback_data=CommonMenuCallback(action="menu")
    )
    builder.adjust(1)
    return builder.as_markup()
