"""Inline keyboards for plan selection (dynamic from API)."""

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.utils.callbacks import CommonMenuCallback, PlanChoiceCallback
from app.utils.formatting import format_plan_button


def plan_selection_keyboard(plans: list[dict]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for plan in plans:
        label = format_plan_button(plan)
        builder.button(
            text=label,
            callback_data=PlanChoiceCallback(plan=str(plan["id"])),
        )
    builder.button(text="⬅️ Назад", callback_data=CommonMenuCallback(action="back"))
    builder.adjust(1)
    return builder.as_markup()
