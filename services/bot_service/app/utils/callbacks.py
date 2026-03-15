"""Callback factories used across the bot."""

from __future__ import annotations

from aiogram.filters.callback_data import CallbackData


class CommonMenuCallback(CallbackData, prefix="cm"):
    action: str


class PlanChoiceCallback(CallbackData, prefix="pl"):
    plan: str


class PaymentMethodCallback(CallbackData, prefix="pm"):
    method: str
    plan: str
    amount: int


class PaymentActionCallback(CallbackData, prefix="pa"):
    action: str
    plan: str
    amount: int


class ReferralActionCallback(CallbackData, prefix="rf"):
    action: str


class SupportActionCallback(CallbackData, prefix="sp"):
    action: str
