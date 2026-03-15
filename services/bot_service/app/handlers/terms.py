"""Handlers for the user agreement flow."""

from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery

from app.keyboards.common import main_menu_keyboard
from app.keyboards.terms import TermsCallback, terms_accept_kb, terms_back_to_menu_kb
from app.texts.start import start_text
from app.texts.terms import TERMS_ACCEPTED_TEXT, TERMS_TEXT

router = Router(name="terms")

ACCEPTED_TERMS_USERS: set[int] = set()


@router.callback_query(TermsCallback.filter(F.action == "accept"))
async def accept_terms(callback_query: CallbackQuery) -> None:
    user_id = callback_query.from_user.id if callback_query.from_user else 0
    if user_id:
        ACCEPTED_TERMS_USERS.add(user_id)
        await callback_query.answer(TERMS_ACCEPTED_TEXT)
    if callback_query.message:
        await callback_query.message.edit_text(
            start_text(),
            reply_markup=main_menu_keyboard(),
            parse_mode="HTML",
        )
    await callback_query.answer()


@router.callback_query(TermsCallback.filter(F.action == "show"))
async def show_terms(callback_query: CallbackQuery) -> None:
    if callback_query.message:
        await callback_query.message.edit_text(
            TERMS_TEXT,
            reply_markup=terms_back_to_menu_kb(),
            parse_mode="HTML",
        )
    await callback_query.answer()


@router.callback_query(TermsCallback.filter(F.action == "back"))
async def terms_back_to_menu(callback_query: CallbackQuery) -> None:
    if callback_query.message:
        await callback_query.message.edit_text(
            start_text(),
            reply_markup=main_menu_keyboard(),
            parse_mode="HTML",
        )
    await callback_query.answer()
