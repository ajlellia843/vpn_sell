"""Inline keyboards for referral and partner programs."""

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from utils.callbacks import CommonMenuCallback, ReferralActionCallback


def referral_program_keyboard() -> InlineKeyboardMarkup:
    """Build a keyboard for the referral program."""

    builder = InlineKeyboardBuilder()
    builder.button(
        text="🚀 Поделиться с друзьями",
        callback_data=ReferralActionCallback(action="share"),
    )
    # builder.button(
    #     text="💼 Партнерская программа",
    #     callback_data=ReferralActionCallback(action="partner"),
    # )
    builder.button(
        text="⤴️ Вернуться в меню", callback_data=CommonMenuCallback(action="menu")
    )
    builder.adjust(1)
    return builder.as_markup()


def partner_program_keyboard() -> InlineKeyboardMarkup:
    """Build a keyboard for the partner program."""

    builder = InlineKeyboardBuilder()
    # builder.button(
    #     text="🚀 Поделиться с друзьями",
    #     callback_data=ReferralActionCallback(action="share"),
    # )
    # builder.button(
    #     text="🤝 Реферальная программа",
    #     callback_data=ReferralActionCallback(action="referral"),
    # )
    # builder.button(
    #     text="⤴️ Вернуться в меню", callback_data=CommonMenuCallback(action="menu")
    # )
    builder.adjust(1)
    return builder.as_markup()
