"""Inline keyboards for the support section."""

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from utils.callbacks import CommonMenuCallback, SupportActionCallback


def support_menu_keyboard() -> InlineKeyboardMarkup:
    """Build a keyboard for support actions."""

    builder = InlineKeyboardBuilder()
    builder.button(
        text="📔 Инструкция", callback_data=SupportActionCallback(action="instructions")
    )
    builder.button(text="📖 FAQ", callback_data=SupportActionCallback(action="faq"))
    builder.button(
        text="✏️ Задать вопрос", callback_data=SupportActionCallback(action="ask")
    )
    builder.button(text="⬅️ Вернуться в меню", callback_data=CommonMenuCallback(action="back"))
    builder.adjust(1)
    return builder.as_markup()
