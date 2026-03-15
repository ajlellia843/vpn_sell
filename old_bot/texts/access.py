"""Texts for access activation and key delivery."""

from __future__ import annotations

ACCESS_ACTIVATED_TEXTS: dict[str, str] = {
    "ru": "✅ Доступ активирован! Подписка успешно оформлена.",
    "en": "✅ Access activated! Your subscription is now active.",
}

ACCESS_KEY_TEXTS: dict[str, str] = {
    "ru": (
        "🔐 Ниже — ваш ключ подключения к VPN. Сохраните его: он понадобится "
        "для настройки на всех устройствах."
    ),
    "en": (
        "🔐 Below is your VPN connection key. Keep it safe — you will need "
        "it to set up VPN on all your devices."
    ),
}

INSTRUCTIONS_REMINDER_TEXTS: dict[str, str] = {
    "ru": "ℹ️ Инструкцию подключения вы всегда найдёте в главном меню «❓ Как установить?».",
    "en": "ℹ️ You can always find the setup guide in the main menu «❓ How to install?».",
}


def access_activated_text(lang: str = "ru") -> str:
    """Return the activation success message."""
    return ACCESS_ACTIVATED_TEXTS.get(lang, ACCESS_ACTIVATED_TEXTS["ru"])


def access_key_text(lang: str = "ru") -> str:
    """Return the key delivery message."""
    return ACCESS_KEY_TEXTS.get(lang, ACCESS_KEY_TEXTS["ru"])


def instructions_reminder_text(lang: str = "ru") -> str:
    """Return the reminder on where to find setup instructions."""
    return INSTRUCTIONS_REMINDER_TEXTS.get(lang, INSTRUCTIONS_REMINDER_TEXTS["ru"])
