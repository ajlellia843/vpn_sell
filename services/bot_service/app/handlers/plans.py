from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from app.keyboards.inline import confirm_keyboard, payment_keyboard
from app.keyboards.plans import plans_keyboard
from app.services.api_client import APIClient, APIError
from app.utils.formatting import format_plan

router = Router(name="plans")


@router.message(F.text == "🔑 Тарифы")
async def show_plans(message: Message) -> None:
    api: APIClient = message.bot["api_client"]  # type: ignore[index]
    try:
        plans = await api.get_plans()
    except APIError:
        await message.answer("Не удалось загрузить тарифы. Попробуйте позже.")
        return

    if not plans:
        await message.answer("Тарифы временно недоступны.")
        return

    await message.answer("Выберите тариф:", reply_markup=plans_keyboard(plans))


@router.callback_query(F.data.startswith("plan:"))
async def select_plan(callback: CallbackQuery) -> None:
    api: APIClient = callback.bot["api_client"]  # type: ignore[index]
    plan_id = callback.data.split(":", 1)[1]  # type: ignore[union-attr]

    try:
        plans = await api.get_plans()
    except APIError:
        await callback.answer("Ошибка загрузки", show_alert=True)
        return

    plan = next((p for p in plans if str(p["id"]) == plan_id), None)
    if plan is None:
        await callback.answer("Тариф не найден", show_alert=True)
        return

    text = format_plan(plan) + "\n\nПодтвердить выбор?"
    await callback.message.edit_text(  # type: ignore[union-attr]
        text,
        reply_markup=confirm_keyboard(f"confirm_plan:{plan_id}"),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("confirm_plan:"))
async def confirm_plan(callback: CallbackQuery) -> None:
    api: APIClient = callback.bot["api_client"]  # type: ignore[index]
    plan_id = callback.data.split(":", 1)[1]  # type: ignore[union-attr]
    user = callback.from_user

    try:
        order = await api.create_order(telegram_id=user.id, plan_id=plan_id)
    except APIError:
        await callback.answer("Не удалось создать заказ", show_alert=True)
        return

    payment_url = order.get("payment_url", "")
    order_id = str(order["id"])

    await callback.message.edit_text(  # type: ignore[union-attr]
        "Заказ создан! Перейдите к оплате:",
        reply_markup=payment_keyboard(payment_url, order_id),
    )
    await callback.answer()


@router.callback_query(F.data == "cancel")
async def cancel_action(callback: CallbackQuery) -> None:
    await callback.message.delete()  # type: ignore[union-attr]
    await callback.answer("Отменено")
