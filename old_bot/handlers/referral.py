"""Handlers for referral and partner program callbacks."""

from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery

# from keyboards.referral import partner_program_keyboard
# from texts.referral import partner_program_text
from utils.callbacks import ReferralActionCallback

router = Router()


# @router.callback_query(ReferralActionCallback.filter(F.action == "partner"))
# async def show_partner_program(callback_query: CallbackQuery) -> None:
#     """Show the partner program screen."""
#     link = "https://t.me/your_bot?start=partner"
#     partner_text = partner_program_text(
#         link=link,
#         transitions=0,
#         purchases=0,
#         profit="0 ₽",
#         available="0 ₽",
#         conversion="0%",
#     )
#     if callback_query.message:
#         await callback_query.message.edit_text(
#             partner_text,
#             reply_markup=partner_program_keyboard(),
#             parse_mode="HTML",
#         )
#     await callback_query.answer()
