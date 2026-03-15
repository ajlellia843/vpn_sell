"""Handlers for the /start command and main menu navigation."""

from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message

from keyboards.common import (
    install_guide_keyboard,
    locations_menu_keyboard,
    main_menu_keyboard,
    menu_keyboard,
)
from keyboards.plans import plan_selection_keyboard
from keyboards.referral import referral_program_keyboard
from keyboards.support import support_menu_keyboard
from texts.locations import locations_text
from texts.payments import buy_text, free_trial_text
from texts.referral import referral_program_text
from texts.start import start_text
from texts.instructions import install_guide_text
from texts.support import support_text
from utils.callbacks import CommonMenuCallback, ReferralActionCallback

router = Router()


@router.message(CommandStart())
async def start_command(message: Message) -> None:
    """Handle the /start command."""
    await message.answer(
        start_text(),
        reply_markup=main_menu_keyboard(),
        parse_mode="HTML",
    )


@router.callback_query(CommonMenuCallback.filter(F.action == "menu"))
@router.callback_query(CommonMenuCallback.filter(F.action == "back"))
async def back_to_menu(callback_query: CallbackQuery) -> None:
    """Return to the main menu from any screen."""
    if callback_query.message:
        await callback_query.message.edit_text(
            start_text(),
            reply_markup=main_menu_keyboard(),
            parse_mode="HTML",
        )
    await callback_query.answer()


@router.callback_query(CommonMenuCallback.filter(F.action == "get_vpn"))
async def show_purchase_screen(callback_query: CallbackQuery) -> None:
    """Show the purchase flow entry point."""
    if callback_query.message:
        await callback_query.message.edit_text(
            buy_text(),
            reply_markup=plan_selection_keyboard(),
            parse_mode="HTML",
        )
    await callback_query.answer()


@router.callback_query(CommonMenuCallback.filter(F.action == "locations"))
async def show_locations(callback_query: CallbackQuery) -> None:
    """Show available VPN locations."""
    if callback_query.message:
        await callback_query.message.edit_text(
            locations_text(),
            reply_markup=locations_menu_keyboard(),
            parse_mode="HTML",
        )
    await callback_query.answer()


@router.callback_query(ReferralActionCallback.filter(F.action == "referral"))
async def show_referral(callback_query: CallbackQuery) -> None:
    """Show the referral program information."""
    user_id = callback_query.from_user.id if callback_query.from_user else 0
    link = f"https://t.me/meshochek_vpn_bot?start=ref{user_id}"
    referral_text = referral_program_text(
        link=link,
        invited=0,
        paid=0,
        available_months="0 мес.",
    )
    if callback_query.message:
        await callback_query.message.edit_text(
            referral_text,
            reply_markup=referral_program_keyboard(),
            parse_mode="HTML",
        )
    await callback_query.answer()


@router.callback_query(CommonMenuCallback.filter(F.action == "help"))
async def show_support(callback_query: CallbackQuery) -> None:
    """Show the support screen."""
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
    """Show the installation guide screen."""
    if callback_query.message:
        await callback_query.message.edit_text(
            install_guide_text(),
            reply_markup=install_guide_keyboard(),
        )
    await callback_query.answer()

@router.callback_query(CommonMenuCallback.filter(F.action == "trial"))
async def show_free_trial(callback_query: CallbackQuery) -> None:
    """Show the free trial placeholder."""
    if callback_query.message:
        await callback_query.message.edit_text(
            free_trial_text(),
            reply_markup=menu_keyboard(),
            parse_mode="HTML",
        )
    await callback_query.answer()
