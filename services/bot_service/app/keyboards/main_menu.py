from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def main_menu_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔑 Тарифы"), KeyboardButton(text="📱 Моя подписка")],
            [KeyboardButton(text="❓ Помощь")],
        ],
        resize_keyboard=True,
    )
