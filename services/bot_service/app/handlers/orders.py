from aiogram import F, Router
from aiogram.types import CallbackQuery

from app.services.api_client import APIClient, APIError

router = Router(name="orders")

_STATUS_MAP: dict[str, str] = {
    "paid": "✅ Оплата подтверждена! Ваша подписка активна.",
    "pending": "⏳ Оплата ещё не поступила. Попробуйте позже.",
    "failed": "❌ Оплата не прошла.",
    "cancelled": "❌ Заказ отменён.",
}


@router.callback_query(F.data.startswith("check_payment:"))
async def check_payment(callback: CallbackQuery) -> None:
    api: APIClient = callback.bot["api_client"]  # type: ignore[index]
    order_id = callback.data.split(":", 1)[1]  # type: ignore[union-attr]

    try:
        order = await api.get_order(order_id)
    except APIError:
        await callback.answer("Не удалось проверить статус", show_alert=True)
        return

    status = order.get("status", "pending")
    text = _STATUS_MAP.get(status, f"Статус заказа: {status}")
    await callback.answer(text, show_alert=True)
