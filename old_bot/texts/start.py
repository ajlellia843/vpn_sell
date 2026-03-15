"""Texts for the /start command and main menu."""

from __future__ import annotations

START_TEXTS: dict[str, str] = {
    "ru": (
        "<b>Meshochek VPN</b> откроет доступ к свободному интернету с любого "
        "устройства.\n\n"
        "📱 Доступ к Instagram, TikTok, Facebook, Twitter и другим недоступным "
        "ресурсам\n\n"
        "🚀 Высокая скорость, безлимитный трафик и низкие цены\n\n"
        "⚡ Оперативная и дружелюбная поддержка. Поможем настроить VPN легко "
        "и просто\n\n"
        "💳 Оплата российскими картами и криптовалютами\n\n"
        "🎬 Доступ к сервисам, недоступным в вашей стране по выгодным ценам "
        "(Netflix, Spotify, Apple)\n\n"
        "Кстати, у нас есть <a href=\"https://t.me/meshochek_vpn\">"
        "Telegram-канал</a>, где мы пишем о новостях из мира IT.\n\n"
        "Пользовательское соглашение"
    ),
    "en": (
        "<b>Meshochek VPN</b> unlocks free internet on any device.\n\n"
        "📱 Access to Instagram, TikTok, Facebook, X (Twitter), and other "
        "blocked services\n\n"
        "🚀 High speed, unlimited traffic, and fair prices\n\n"
        "⚡ Fast and friendly support. We help you set up VPN easily\n\n"
        "💳 Pay with bank cards or cryptocurrencies\n\n"
        "🎬 Get access to services not available in your country at great "
        "prices (Netflix, Spotify, Apple)\n\n"
        "By the way, we have a <a href=\"https://t.me/meshochek_vpn\">"
        "Telegram channel</a> with IT news."
    ),
}


def start_text(lang: str = "ru") -> str:
    """Return the main menu text in the selected language."""
    return START_TEXTS.get(lang, START_TEXTS["ru"])
