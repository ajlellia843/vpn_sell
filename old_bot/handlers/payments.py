"""Handlers for payment flows."""

from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery

from keyboards.common import menu_keyboard
from keyboards.payments import payment_link_keyboard, payment_methods_keyboard
from texts.payments import (
    checkout_text,
    payment_methods_text,
    payment_placeholder_text,
)
from utils.callbacks import PaymentActionCallback, PaymentMethodCallback
from handlers.plans import PLAN_OPTIONS

router = Router()


@router.callback_query(PaymentActionCallback.filter(F.action == "methods"))
async def show_payment_methods(
    callback_query: CallbackQuery, callback_data: PaymentActionCallback
) -> None:
    """Show the available payment methods."""
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
    """Show confirmation screen for selected payment method."""
    plan_label, amount_rub = PLAN_OPTIONS.get(callback_data.plan, ("", 0))
    if callback_query.message:
        await callback_query.message.edit_text(
            checkout_text(plan_label, callback_data.amount or amount_rub),
            reply_markup=payment_link_keyboard(
                plan=callback_data.plan,
                amount_rub=callback_data.amount or amount_rub,
            ),
            parse_mode="HTML",
        )
    await callback_query.answer()


@router.callback_query(PaymentActionCallback.filter(F.action == "pay"))
async def show_payment_placeholder(
    callback_query: CallbackQuery, callback_data: PaymentActionCallback
) -> None:
    """Show placeholder for payment integration."""
    if callback_query.message:
        await callback_query.message.edit_text(
            payment_placeholder_text(),
            reply_markup=menu_keyboard(),
            parse_mode="HTML",
        )
    await callback_query.answer()
