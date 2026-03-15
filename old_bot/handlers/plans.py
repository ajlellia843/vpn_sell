"""Handlers for subscription plans."""

from __future__ import annotations

from aiogram import Router
from aiogram.types import CallbackQuery

from keyboards.payments import payment_methods_keyboard
from texts.payments import payment_methods_text
from utils.callbacks import PlanChoiceCallback

router = Router()

PLAN_OPTIONS: dict[str, tuple[str, int]] = {
    "12m": ("1 год", 2690),
    "6m": ("6 месяцев", 1390),
    "3m": ("3 месяца", 790),
    "1m": ("1 месяц", 299),
}


@router.callback_query(PlanChoiceCallback.filter())
async def handle_plan_choice(
    callback_query: CallbackQuery, callback_data: PlanChoiceCallback
) -> None:
    """Handle plan selection and show payment methods."""
    _, amount_rub = PLAN_OPTIONS.get(callback_data.plan, ("", 0))
    if callback_query.message:
        await callback_query.message.edit_text(
            payment_methods_text(),
            reply_markup=payment_methods_keyboard(
                plan=callback_data.plan,
                amount_rub=amount_rub,
            ),
            parse_mode="HTML",
        )
    await callback_query.answer()
