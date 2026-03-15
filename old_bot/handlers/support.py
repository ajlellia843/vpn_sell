"""Handlers for support navigation."""

from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery

from keyboards.common import menu_keyboard
from texts.support import ask_question_text, faq_text
from utils.callbacks import SupportActionCallback

router = Router()


@router.callback_query(SupportActionCallback.filter(F.action == "ask"))
async def handle_ask_question(callback_query: CallbackQuery) -> None:
    """Show the ask question placeholder."""
    if callback_query.message:
        await callback_query.message.edit_text(
            ask_question_text(),
            reply_markup=menu_keyboard(),
            parse_mode="HTML",
        )
    await callback_query.answer()


@router.callback_query(SupportActionCallback.filter(F.action == "faq"))
async def handle_faq(callback_query: CallbackQuery) -> None:
    """Show the FAQ placeholder."""
    if callback_query.message:
        await callback_query.message.edit_text(
            faq_text(),
            reply_markup=menu_keyboard(),
            parse_mode="HTML",
        )
    await callback_query.answer()
