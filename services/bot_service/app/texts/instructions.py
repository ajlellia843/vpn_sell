"""Short setup instructions per platform."""

from __future__ import annotations

IOS_INSTRUCTIONS: dict[str, str] = {
    "ru": (
        "<b>iOS — краткая инструкция</b>\n\n"
        "1) Скопируйте ключ подключения.\n"
        "2) Откройте приложение VPN по своему выбору.\n"
        "3) Добавьте новый профиль и вставьте ключ.\n"
        "4) Сохраните профиль и включите VPN.\n"
        "5) Проверьте, что соединение активно."
    ),
    "en": (
        "<b>iOS — quick setup</b>\n\n"
        "1) Copy your connection key.\n"
        "2) Open any VPN app you prefer.\n"
        "3) Add a new profile and paste the key.\n"
        "4) Save the profile and turn VPN on.\n"
        "5) Make sure the connection is active."
    ),
}

ANDROID_INSTRUCTIONS: dict[str, str] = {
    "ru": (
        "<b>Android — краткая инструкция</b>\n\n"
        "1) Скопируйте ключ подключения.\n"
        "2) Запустите VPN-приложение.\n"
        "3) Создайте профиль и вставьте ключ.\n"
        "4) Сохраните настройки и подключитесь.\n"
        "5) Убедитесь, что VPN включён."
    ),
    "en": (
        "<b>Android — quick setup</b>\n\n"
        "1) Copy your connection key.\n"
        "2) Open your VPN app.\n"
        "3) Create a profile and paste the key.\n"
        "4) Save settings and connect.\n"
        "5) Confirm that VPN is active."
    ),
}

WINDOWS_INSTRUCTIONS: dict[str, str] = {
    "ru": (
        "<b>Windows — краткая инструкция</b>\n\n"
        "1) Скопируйте ключ подключения.\n"
        "2) Установите и откройте VPN-клиент.\n"
        "3) Импортируйте или добавьте новый профиль.\n"
        "4) Вставьте ключ и сохраните.\n"
        "5) Подключитесь к VPN."
    ),
    "en": (
        "<b>Windows — quick setup</b>\n\n"
        "1) Copy your connection key.\n"
        "2) Install and open a VPN client.\n"
        "3) Import or add a new profile.\n"
        "4) Paste the key and save.\n"
        "5) Connect to the VPN."
    ),
}

MACOS_INSTRUCTIONS: dict[str, str] = {
    "ru": (
        "<b>macOS — краткая инструкция</b>\n\n"
        "1) Скопируйте ключ подключения.\n"
        "2) Откройте VPN-приложение или клиент.\n"
        "3) Добавьте новый профиль.\n"
        "4) Вставьте ключ и сохраните.\n"
        "5) Включите VPN и проверьте статус."
    ),
    "en": (
        "<b>macOS — quick setup</b>\n\n"
        "1) Copy your connection key.\n"
        "2) Open a VPN app or client.\n"
        "3) Add a new profile.\n"
        "4) Paste the key and save.\n"
        "5) Turn VPN on and check the status."
    ),
}

INSTRUCTIONS_OVERVIEW_TEXTS: dict[str, str] = {
    "ru": (
        "📘 <b>Инструкции по подключению</b>\n\n"
        "Мы подготовили краткие инструкции для популярных платформ:\n"
        "• iOS\n"
        "• Android\n"
        "• Windows\n"
        "• macOS\n\n"
        "Если нужна помощь — напишите в поддержку."
    ),
    "en": (
        "📘 <b>Setup instructions</b>\n\n"
        "We have prepared quick guides for popular platforms:\n"
        "• iOS\n"
        "• Android\n"
        "• Windows\n"
        "• macOS\n\n"
        "If you need help, contact support."
    ),
}


def ios_instructions(lang: str = "ru") -> str:
    return IOS_INSTRUCTIONS.get(lang, IOS_INSTRUCTIONS["ru"])


def android_instructions(lang: str = "ru") -> str:
    return ANDROID_INSTRUCTIONS.get(lang, ANDROID_INSTRUCTIONS["ru"])


def windows_instructions(lang: str = "ru") -> str:
    return WINDOWS_INSTRUCTIONS.get(lang, WINDOWS_INSTRUCTIONS["ru"])


def macos_instructions(lang: str = "ru") -> str:
    return MACOS_INSTRUCTIONS.get(lang, MACOS_INSTRUCTIONS["ru"])


def instructions_overview_text(lang: str = "ru") -> str:
    return INSTRUCTIONS_OVERVIEW_TEXTS.get(lang, INSTRUCTIONS_OVERVIEW_TEXTS["ru"])


INSTALL_GUIDE_TEXTS: dict[str, str] = {
    "ru": (
        "Как установить.\n\n"
        "1. Скачайте приложение v2RayTun на ваше устройство, для этого кликните на соответствующую кнопку внизу\n"
        "2. После установки скопируйте ключ, который мы вам выдали.\n"
        "3. Откройте v2RayTun.\n"
        "4. Нажмите сверху на знак плюс.\n"
        "5. В появившемся окне нажмите на \"Custom config\".\n"
        "6. Затем нажмите на \"Import custom config from URL\".\n"
        "7. После этого у вас появится в списке наш VPN, нажмите на него, затем на кнопку включить по центру.\n"
        "8. Вы включили его. Приятного пользования"
    ),
    "en": (
        "How to install.\n\n"
        "1. Download the v2RayTun app to your device using the button below.\n"
        "2. After installation, copy the key we provided to you.\n"
        "3. Open v2RayTun.\n"
        "4. Tap the plus sign at the top.\n"
        "5. In the opened window, tap \"Custom config\".\n"
        "6. Then tap \"Import custom config from URL\".\n"
        "7. After that, our VPN will appear in the list: tap it, then tap the connect button in the center.\n"
        "8. Done. Enjoy using it"
    ),
}


def install_guide_text(lang: str = "ru") -> str:
    return INSTALL_GUIDE_TEXTS.get(lang, INSTALL_GUIDE_TEXTS["ru"])
