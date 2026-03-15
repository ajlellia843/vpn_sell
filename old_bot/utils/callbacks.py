"""Callback factories used across the bot."""

from __future__ import annotations

from aiogram.filters.callback_data import CallbackData


class CommonMenuCallback(CallbackData, prefix="cm"):
    """Callback data for common menu actions."""

    action: str


class PlanChoiceCallback(CallbackData, prefix="pl"):
    """Callback data for plan choices."""

    plan: str


class PaymentMethodCallback(CallbackData, prefix="pm"):
    """Callback data for payment method selection."""

    method: str
    plan: str
    amount: int


class PaymentActionCallback(CallbackData, prefix="pa"):
    """Callback data for payment actions."""

    action: str
    plan: str
    amount: int


class ReferralActionCallback(CallbackData, prefix="rf"):
    """Callback data for referral actions."""

    action: str


class SupportActionCallback(CallbackData, prefix="sp"):
    """Callback data for support actions."""

    action: str
