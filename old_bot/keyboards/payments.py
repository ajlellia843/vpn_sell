"""Inline keyboards for payment flows."""

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from utils.callbacks import (
    CommonMenuCallback,
    PaymentActionCallback,
    PaymentMethodCallback,
)


def payment_methods_keyboard(plan: str, amount_rub: int) -> InlineKeyboardMarkup:
    """Build a keyboard for payment method selection."""

    builder = InlineKeyboardBuilder()
    builder.button(
        text="💳 Банковской картой (YooKassa)",
        callback_data=PaymentMethodCallback(
            method="card",
            plan=plan,
            amount=amount_rub,
        ),
    )
    builder.button(
        text="Криптовалютой",
        callback_data=PaymentMethodCallback(
            method="crypto",
            plan=plan,
            amount=amount_rub,
        ),
    )
    builder.button(
        text="⬅️ Назад",
        callback_data=CommonMenuCallback(action="get_vpn"),
    )
    builder.adjust(1)
    return builder.as_markup()


def payment_link_keyboard(plan: str, amount_rub: int) -> InlineKeyboardMarkup:
    """Build a keyboard to proceed to payment."""

    builder = InlineKeyboardBuilder()
    builder.button(
        text="💳 Перейти к оплате",
        callback_data=PaymentActionCallback(
            action="pay",
            plan=plan,
            amount=amount_rub,
        ),
    )
    builder.button(
        text="⬅️ Назад",
        callback_data=PaymentActionCallback(
            action="methods",
            plan=plan,
            amount=amount_rub,
        ),
    )
    builder.adjust(1)
    return builder.as_markup()
