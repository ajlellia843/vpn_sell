from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def plans_keyboard(plans: list[dict]) -> InlineKeyboardMarkup:
    buttons: list[list[InlineKeyboardButton]] = []
    for plan in plans:
        text = f"{plan['name']} — {plan['price']} {plan.get('currency', '₽')} / {plan['duration_days']} дней"
        buttons.append(
            [InlineKeyboardButton(text=text, callback_data=f"plan:{plan['id']}")]
        )
    return InlineKeyboardMarkup(inline_keyboard=buttons)
