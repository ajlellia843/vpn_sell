"""Texts for available VPN locations."""

from __future__ import annotations

LOCATIONS_TEXTS: dict[str, str] = {
    "ru": (
        "📍 <b>Доступные локации</b>\n\n"
        "💬 Каждая локация подключена как минимум к 1Gbps каналу и "
        "оптимизирована для работы на максимальной скорости.\n\n"
        "🇦🇹 Австрия (Вена)\n\n"
        "🇨🇿 Чехия (Прага)\n\n"
        "🇫🇮 Финляндия (Хельсинки)\n\n"
        "🇫🇷 Франция (Париж)\n\n"
        "🇰🇿 Казахстан (Алматы)\n\n"
        "🇱🇻 Латвия (Рига)\n\n"
        "🇳🇱 Нидерланды (Амстердам)\n\n"
        "🇵🇱 Польша (Варшава)\n\n"
        "🇷🇺 Россия (Москва)\n\n"
        "🏳️ Обход белого списка\n\n"
        "🇸🇪 Швеция (Стокгольм)\n\n"
        "🇹🇷 Турция (Стамбул)\n\n"
        "🇬🇧 Великобритания (Лондон)\n\n"
        "🇺🇸 США (Нью-Йорк)"
    ),
    "en": (
        "📍 <b>Available locations</b>\n\n"
        "💬 Each location is connected to at least a 1Gbps channel and "
        "optimized for maximum speed.\n\n"
        "🇦🇹 Austria (Vienna)\n\n"
        "🇨🇿 Czechia (Prague)\n\n"
        "🇫🇮 Finland (Helsinki)\n\n"
        "🇫🇷 France (Paris)\n\n"
        "🇰🇿 Kazakhstan (Almaty)\n\n"
        "🇱🇻 Latvia (Riga)\n\n"
        "🇳🇱 Netherlands (Amsterdam)\n\n"
        "🇵🇱 Poland (Warsaw)\n\n"
        "🇷🇺 Russia (Moscow)\n\n"
        "🏳️ Bypass allowlist\n\n"
        "🇸🇪 Sweden (Stockholm)\n\n"
        "🇹🇷 Turkey (Istanbul)\n\n"
        "🇬🇧 United Kingdom (London)\n\n"
        "🇺🇸 USA (New York)"
    ),
}


def locations_text(lang: str = "ru") -> str:
    """Return the available locations text."""
    return LOCATIONS_TEXTS.get(lang, LOCATIONS_TEXTS["ru"])
