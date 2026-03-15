"""Inline keyboards for plan selection."""

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from utils.callbacks import CommonMenuCallback, PlanChoiceCallback


def plan_selection_keyboard() -> InlineKeyboardMarkup:
    """Build a keyboard for plan selection."""

    builder = InlineKeyboardBuilder()
    builder.button(
        text="🔑 1 год: 2690 руб.", callback_data=PlanChoiceCallback(plan="12m")
    )
    builder.button(
        text="🔑 6 месяцев: 1390 руб.", callback_data=PlanChoiceCallback(plan="6m")
    )
    builder.button(
        text="🔑 3 месяца: 790 руб.", callback_data=PlanChoiceCallback(plan="3m")
    )
    builder.button(
        text="🔑 1 месяц: 299 руб.", callback_data=PlanChoiceCallback(plan="1m")
    )
    builder.button(text="⬅️ Назад", callback_data=CommonMenuCallback(action="back"))
    builder.adjust(1)
    return builder.as_markup()
