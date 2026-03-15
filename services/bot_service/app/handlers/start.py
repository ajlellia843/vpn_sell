from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.keyboards.main_menu import main_menu_kb
from app.services.api_client import APIClient, APIError

router = Router(name="start")

_WELCOME = "Добро пожаловать! Я помогу вам с VPN подпиской.\n\nВыберите действие:"


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    api: APIClient = message.bot["api_client"]  # type: ignore[index]
    user = message.from_user
    if user:
        try:
            await api.get_me(
                telegram_id=user.id,
                username=user.username,
                first_name=user.first_name,
            )
        except APIError:
            pass
    await message.answer(_WELCOME, reply_markup=main_menu_kb())
