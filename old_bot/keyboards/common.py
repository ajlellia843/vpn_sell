"""Common inline keyboards for the bot."""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from utils.callbacks import CommonMenuCallback, ReferralActionCallback


def main_menu_keyboard() -> InlineKeyboardMarkup:
    """Build the main menu inline keyboard."""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="🔒 Получить VPN 🔒", callback_data=CommonMenuCallback(action="get_vpn").pack())
    )
    builder.row(
        InlineKeyboardButton(text="📍 Доступные локации", callback_data=CommonMenuCallback(action="locations").pack())
    )
    builder.row(
        InlineKeyboardButton(text="🙋 Пригласить", callback_data=ReferralActionCallback(action="referral").pack()),
        InlineKeyboardButton(text="❓ Помощь", callback_data=CommonMenuCallback(action="help").pack()),
    )
    builder.row(
        InlineKeyboardButton(text="🎁 Попробовать БЕСПЛАТНО", callback_data=CommonMenuCallback(action="trial").pack())
    )
    builder.row(
        InlineKeyboardButton(text="Как установить", callback_data=CommonMenuCallback(action="how_install").pack())
    )

    return builder.as_markup()

def back_keyboard() -> InlineKeyboardMarkup:
    """Build a keyboard with a single back button."""

    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ Назад", callback_data=CommonMenuCallback(action="back"))
    return builder.as_markup()


def menu_keyboard() -> InlineKeyboardMarkup:
    """Build a keyboard with a single return-to-menu button."""

    builder = InlineKeyboardBuilder()
    builder.button(
        text="⤴️ Вернуться в меню", callback_data=CommonMenuCallback(action="menu")
    )
    return builder.as_markup()


def locations_menu_keyboard() -> InlineKeyboardMarkup:
    """Build a keyboard for the available locations screen."""

    return menu_keyboard()


def install_guide_keyboard() -> InlineKeyboardMarkup:
    """Build a keyboard for the installation guide screen."""

    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="Android",
            url="https://play.google.com/store/apps/details?id=com.v2raytun.android",
        ),
        InlineKeyboardButton(
            text="Windows",
            url="https://storage.v2raytun.com/v2RayTun_Setup.exe",
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text="iPhone",
            url="https://apps.apple.com/en/app/v2raytun/id6476628951",
        ),
        InlineKeyboardButton(
            text="iPad",
            url="https://apps.apple.com/en/app/v2raytun/id6476628951",
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text="MacBook",
            url="https://apps.apple.com/en/app/v2raytun/id6476628951",
        ),
        InlineKeyboardButton(
            text="Android TV",
            url="https://play.google.com/store/apps/details?id=com.v2raytun.android",
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text="Назад",
            callback_data=CommonMenuCallback(action="back").pack(),
        )
    )
    return builder.as_markup()
