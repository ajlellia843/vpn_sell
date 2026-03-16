"""Handlers for subscription plan selection (dynamic from API)."""

from __future__ import annotations

import structlog
from aiogram import Router
from aiogram.types import CallbackQuery

from app.keyboards.payments import payment_methods_keyboard
from app.services.api_client import APIClient, APIError
from app.texts.payments import payment_methods_text
from app.utils.callbacks import PlanChoiceCallback

logger = structlog.get_logger(__name__)

router = Router(name="plans")

_plan_cache: dict[str, dict] = {}


@router.callback_query(PlanChoiceCallback.filter())
async def handle_plan_choice(
    callback_query: CallbackQuery, callback_data: PlanChoiceCallback, api_client: APIClient
) -> None:
    plan_id = callback_data.plan

    plan = _plan_cache.get(plan_id)
    if not plan:
        try:
            plans = await api_client.get_plans()
            for p in plans:
                _plan_cache[str(p["id"])] = p
            plan = _plan_cache.get(plan_id)
        except APIError:
            plan = None

    amount_rub = int(plan["price"]) if plan else 0

    if callback_query.message:
        await callback_query.message.edit_text(
            payment_methods_text(),
            reply_markup=payment_methods_keyboard(plan=plan_id, amount_rub=amount_rub),
            parse_mode="HTML",
        )
    await callback_query.answer()
