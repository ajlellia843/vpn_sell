"""Handlers for payment flows — real API integration."""

from __future__ import annotations

import structlog
from aiogram import F, Router
from aiogram.types import CallbackQuery

from app.keyboards.common import menu_keyboard
from app.keyboards.payments import payment_checkout_keyboard, payment_methods_keyboard
from app.services.api_client import APIClient, APIError
from app.texts.payments import payment_methods_text, proceed_to_payment_text
from app.texts.access import access_activated_text, access_key_text
from app.utils.callbacks import PaymentActionCallback, PaymentMethodCallback
logger = structlog.get_logger(__name__)

router = Router(name="payments")


def _api(bot) -> APIClient:  # noqa: ANN001
    return bot["api_client"]


@router.callback_query(PaymentActionCallback.filter(F.action == "methods"))
async def show_payment_methods(
    callback_query: CallbackQuery, callback_data: PaymentActionCallback
) -> None:
    if callback_query.message:
        await callback_query.message.edit_text(
            payment_methods_text(),
            reply_markup=payment_methods_keyboard(
                plan=callback_data.plan,
                amount_rub=callback_data.amount,
            ),
            parse_mode="HTML",
        )
    await callback_query.answer()


@router.callback_query(PaymentMethodCallback.filter())
async def handle_payment_method(
    callback_query: CallbackQuery, callback_data: PaymentMethodCallback
) -> None:
    telegram_id = callback_query.from_user.id if callback_query.from_user else 0
    plan_id = callback_data.plan
    amount_rub = callback_data.amount

    try:
        order = await _api(callback_query.bot).create_order(telegram_id, plan_id)
        payment_url = order.get("payment_url", "")
        order_id = str(order.get("id", ""))
    except APIError as exc:
        logger.error("create_order_failed", plan=plan_id, error=str(exc))
        payment_url = ""
        order_id = ""

    if payment_url and order_id and callback_query.message:
        await callback_query.message.edit_text(
            proceed_to_payment_text(
                period_label=f"{amount_rub} руб.",
                amount_label=f"{amount_rub} руб.",
            ),
            reply_markup=payment_checkout_keyboard(payment_url, order_id),
            parse_mode="HTML",
        )
    elif callback_query.message:
        await callback_query.message.edit_text(
            "Не удалось создать заказ. Попробуйте позже.",
            reply_markup=menu_keyboard(),
            parse_mode="HTML",
        )
    await callback_query.answer()


@router.callback_query(F.data.startswith("check_payment:"))
async def check_payment(callback_query: CallbackQuery) -> None:
    order_id = (callback_query.data or "").split(":", 1)[-1]
    if not order_id:
        await callback_query.answer("Заказ не найден")
        return

    try:
        order = await _api(callback_query.bot).get_order(order_id)
    except APIError:
        await callback_query.answer("Ошибка проверки. Попробуйте позже.")
        return

    status = order.get("status", "unknown")

    if status == "paid":
        if callback_query.message:
            await callback_query.message.edit_text(
                f"{access_activated_text()}\n\n{access_key_text()}",
                reply_markup=menu_keyboard(),
                parse_mode="HTML",
            )
        await callback_query.answer("Оплата подтверждена!")
    elif status == "pending":
        await callback_query.answer("Оплата ещё не поступила. Подождите немного.", show_alert=True)
    else:
        if callback_query.message:
            await callback_query.message.edit_text(
                f"Статус заказа: {status}",
                reply_markup=menu_keyboard(),
                parse_mode="HTML",
            )
        await callback_query.answer()
