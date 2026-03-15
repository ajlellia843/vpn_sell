from aiogram import F, Router
from aiogram.types import Message

from app.services.api_client import APIClient, APIError
from app.utils.formatting import format_subscription

router = Router(name="subscription")

_HELP_TEXT = (
    "❓ <b>Помощь</b>\n\n"
    "Этот бот помогает управлять VPN подпиской.\n\n"
    "• <b>🔑 Тарифы</b> — выбрать и оплатить тариф\n"
    "• <b>📱 Моя подписка</b> — информация о текущей подписке\n\n"
    "По вопросам обращайтесь: @support"
)


@router.message(F.text == "📱 Моя подписка")
async def show_subscription(message: Message) -> None:
    api: APIClient = message.bot["api_client"]  # type: ignore[index]
    user = message.from_user
    if not user:
        return

    try:
        data = await api.get_subscription(telegram_id=user.id)
    except APIError:
        await message.answer("Не удалось загрузить информацию о подписке.")
        return

    sub = data.get("subscription")
    vpn = data.get("vpn_access")

    if not sub:
        await message.answer(
            "У вас нет активной подписки. Выберите тариф!",
            parse_mode="HTML",
        )
        return

    await message.answer(format_subscription(sub, vpn), parse_mode="HTML")


@router.message(F.text == "❓ Помощь")
async def show_help(message: Message) -> None:
    await message.answer(_HELP_TEXT, parse_mode="HTML")
