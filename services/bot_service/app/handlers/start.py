"""Handlers for the /start command and main menu navigation."""

from __future__ import annotations

import structlog
from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message

from app.keyboards.common import (
    install_guide_keyboard,
    locations_menu_keyboard,
    main_menu_keyboard,
    menu_keyboard,
)
from app.keyboards.plans import plan_selection_keyboard
from app.keyboards.referral import referral_program_keyboard
from app.keyboards.support import support_menu_keyboard
from app.services.api_client import APIClient, APIError
from app.texts.locations import locations_text
from app.texts.payments import buy_text, free_trial_text
from app.texts.referral import referral_program_text
from app.texts.start import start_text
from app.texts.instructions import install_guide_text
from app.texts.support import support_text
from app.utils.callbacks import CommonMenuCallback, ReferralActionCallback

logger = structlog.get_logger(__name__)

router = Router(name="start")


def _api(bot) -> APIClient:  # noqa: ANN001
    return bot["api_client"]


@router.message(CommandStart())
async def start_command(message: Message) -> None:
    user = message.from_user
    if user:
        try:
            await _api(message.bot).get_me(
                telegram_id=user.id,
                username=user.username,
                first_name=user.first_name,
            )
        except APIError:
            logger.warning("user_register_failed", telegram_id=user.id)
    await message.answer(
        start_text(),
        reply_markup=main_menu_keyboard(),
        parse_mode="HTML",
    )


@router.callback_query(CommonMenuCallback.filter(F.action == "menu"))
@router.callback_query(CommonMenuCallback.filter(F.action == "back"))
async def back_to_menu(callback_query: CallbackQuery) -> None:
    if callback_query.message:
        await callback_query.message.edit_text(
            start_text(),
            reply_markup=main_menu_keyboard(),
            parse_mode="HTML",
        )
    await callback_query.answer()


@router.callback_query(CommonMenuCallback.filter(F.action == "get_vpn"))
async def show_purchase_screen(callback_query: CallbackQuery) -> None:
    try:
        plans = await _api(callback_query.bot).get_plans()
    except APIError:
        plans = []
    if callback_query.message:
        await callback_query.message.edit_text(
            buy_text(),
            reply_markup=plan_selection_keyboard(plans),
            parse_mode="HTML",
        )
    await callback_query.answer()


@router.callback_query(CommonMenuCallback.filter(F.action == "locations"))
async def show_locations(callback_query: CallbackQuery) -> None:
    if callback_query.message:
        await callback_query.message.edit_text(
            locations_text(),
            reply_markup=locations_menu_keyboard(),
            parse_mode="HTML",
        )
    await callback_query.answer()


@router.callback_query(ReferralActionCallback.filter(F.action == "referral"))
async def show_referral(callback_query: CallbackQuery) -> None:
    user_id = callback_query.from_user.id if callback_query.from_user else 0
    link = f"https://t.me/meshochek_vpn_bot?start=ref{user_id}"
    text = referral_program_text(
        link=link,
        invited=0,
        paid=0,
        available_months="0 мес.",
    )
    if callback_query.message:
        await callback_query.message.edit_text(
            text,
            reply_markup=referral_program_keyboard(),
            parse_mode="HTML",
        )
    await callback_query.answer()


@router.callback_query(CommonMenuCallback.filter(F.action == "help"))
async def show_support(callback_query: CallbackQuery) -> None:
    user_id = callback_query.from_user.id if callback_query.from_user else 0
    if callback_query.message:
        await callback_query.message.edit_text(
            support_text(user_id=user_id),
            reply_markup=support_menu_keyboard(),
            parse_mode="HTML",
        )
    await callback_query.answer()


@router.callback_query(CommonMenuCallback.filter(F.action == "how_install"))
async def show_install_guide(callback_query: CallbackQuery) -> None:
    if callback_query.message:
        await callback_query.message.edit_text(
            install_guide_text(),
            reply_markup=install_guide_keyboard(),
        )
    await callback_query.answer()


@router.callback_query(CommonMenuCallback.filter(F.action == "trial"))
async def show_free_trial(callback_query: CallbackQuery) -> None:
    if callback_query.message:
        await callback_query.message.edit_text(
            free_trial_text(),
            reply_markup=menu_keyboard(),
            parse_mode="HTML",
        )
    await callback_query.answer()
