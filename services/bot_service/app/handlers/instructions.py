"""Handlers for setup instructions."""

from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery

from app.keyboards.common import menu_keyboard
from app.texts.instructions import instructions_overview_text
from app.utils.callbacks import SupportActionCallback

router = Router(name="instructions")


@router.callback_query(SupportActionCallback.filter(F.action == "instructions"))
async def show_instructions(callback_query: CallbackQuery) -> None:
    if callback_query.message:
        await callback_query.message.edit_text(
            instructions_overview_text(),
            reply_markup=menu_keyboard(),
            parse_mode="HTML",
        )
    await callback_query.answer()
