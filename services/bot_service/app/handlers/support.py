"""Handlers for support navigation."""

from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery

from app.keyboards.common import menu_keyboard
from app.texts.support import ask_question_text, faq_text
from app.utils.callbacks import SupportActionCallback

router = Router(name="support")


@router.callback_query(SupportActionCallback.filter(F.action == "ask"))
async def handle_ask_question(callback_query: CallbackQuery) -> None:
    if callback_query.message:
        await callback_query.message.edit_text(
            ask_question_text(),
            reply_markup=menu_keyboard(),
            parse_mode="HTML",
        )
    await callback_query.answer()


@router.callback_query(SupportActionCallback.filter(F.action == "faq"))
async def handle_faq(callback_query: CallbackQuery) -> None:
    if callback_query.message:
        await callback_query.message.edit_text(
            faq_text(),
            reply_markup=menu_keyboard(),
            parse_mode="HTML",
        )
    await callback_query.answer()
