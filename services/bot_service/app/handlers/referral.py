"""Handlers for referral and partner program callbacks."""

from __future__ import annotations

from aiogram import Router

from app.utils.callbacks import ReferralActionCallback  # noqa: F401

router = Router(name="referral")
