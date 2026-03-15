"""Inline keyboards for payment flows."""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.utils.callbacks import (
    CommonMenuCallback,
    PaymentActionCallback,
    PaymentMethodCallback,
)


def payment_methods_keyboard(plan: str, amount_rub: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="💳 Банковской картой (YooKassa)",
        callback_data=PaymentMethodCallback(method="card", plan=plan, amount=amount_rub),
    )
    builder.button(
        text="Криптовалютой",
        callback_data=PaymentMethodCallback(method="crypto", plan=plan, amount=amount_rub),
    )
    builder.button(
        text="⬅️ Назад",
        callback_data=CommonMenuCallback(action="get_vpn"),
    )
    builder.adjust(1)
    return builder.as_markup()


def payment_checkout_keyboard(payment_url: str, order_id: str) -> InlineKeyboardMarkup:
    """Keyboard with a real payment URL button and a check-status button."""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="💳 Перейти к оплате", url=payment_url))
    builder.row(
        InlineKeyboardButton(
            text="🔄 Проверить оплату",
            callback_data=f"check_payment:{order_id}",
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="⤴️ Вернуться в меню",
            callback_data=CommonMenuCallback(action="menu").pack(),
        )
    )
    return builder.as_markup()
