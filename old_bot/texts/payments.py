"""Texts for purchase and payment flows."""

from __future__ import annotations

BUY_TEXTS: dict[str, str] = {
    "ru": (
        "📅 <b>Выберите срок подписки</b>\n\n"
        "Чем дольше, тем выгоднее! 😊\n\n"
        "💬 После оплаты вы моментально получите ваш уникальный ключ "
        "подключения к VPN, подробную инструкцию по установке вы можете "
        "найти в главном меню «❓ Как установить?»\n\n"
        "❓ Есть вопрос? Наша служба поддержки готова помочь: просто задайте "
        "его в этом чате."
    ),
    "en": (
        "📅 <b>Select a subscription period</b>\n\n"
        "The longer, the better the price! 😊\n\n"
        "💬 After payment, you will instantly receive your unique VPN "
        "connection key. You can find the setup guide in the main menu "
        "«❓ How to install?»\n\n"
        "❓ Have a question? Our support team is ready to help — just ask here."
    ),
}

PAYMENT_METHODS_TEXTS: dict[str, str] = {
    "ru": (
        "💳 <b>Выберите способ оплаты:</b>\n\n"
        "Подписку можно оплатить банковскими картами (включая карты "
        "российских банков), или криптовалютами.\n\n"
        "❓ Есть вопрос? Наша служба поддержки готова помочь: просто задайте "
        "его в этом чате."
    ),
    "en": (
        "💳 <b>Choose a payment method:</b>\n\n"
        "You can pay with bank cards (including cards issued in Russia) "
        "or cryptocurrencies.\n\n"
        "❓ Have a question? Our support team is ready to help — just ask here."
    ),
}

FREE_TRIAL_TEXTS: dict[str, str] = {
    "ru": (
        "🎁 <b>Бесплатный доступ</b>\n\n"
        "Скоро здесь появится возможность попробовать VPN бесплатно. "
        "Следите за обновлениями!"
    ),
    "en": (
        "🎁 <b>Free trial</b>\n\n"
        "The free trial will be available soon. Stay tuned for updates!"
    ),
}

PAYMENT_PLACEHOLDER_TEXTS: dict[str, str] = {
    "ru": (
        "⏳ <b>Оплата</b>\n\n"
        "Подключение оплаты будет реализовано на следующем этапе."
    ),
    "en": (
        "⏳ <b>Payments</b>\n\n"
        "Payment integration will be implemented in the next stage."
    ),
}


def buy_text(lang: str = "ru") -> str:
    """Return the subscription period selection text."""
    return BUY_TEXTS.get(lang, BUY_TEXTS["ru"])


def payment_methods_text(lang: str = "ru") -> str:
    """Return the payment methods description text."""
    return PAYMENT_METHODS_TEXTS.get(lang, PAYMENT_METHODS_TEXTS["ru"])


def free_trial_text(lang: str = "ru") -> str:
    """Return the free trial placeholder text."""
    return FREE_TRIAL_TEXTS.get(lang, FREE_TRIAL_TEXTS["ru"])


def checkout_text(plan_label: str, amount_rub: int, lang: str = "ru") -> str:
    """Return the checkout text for the selected plan."""
    amount_label = f"{amount_rub} руб."
    return proceed_to_payment_text(plan_label, amount_label, lang=lang)


def payment_placeholder_text(lang: str = "ru") -> str:
    """Return the placeholder text for unavailable payments."""
    return PAYMENT_PLACEHOLDER_TEXTS.get(lang, PAYMENT_PLACEHOLDER_TEXTS["ru"])


def proceed_to_payment_text(
    period_label: str,
    amount_label: str,
    lang: str = "ru",
) -> str:
    """Return the confirmation text before payment."""
    if lang == "en":
        return (
            "📅 Selected subscription period: {period}\n"
            "💸 Amount due: {amount}\n\n"
            "💬 After payment, you will instantly receive your unique VPN "
            "connection key. You can find the setup guide in the main menu "
            "«❓ How to install?»\n\n"
            "❓ Have a question? Our support team is ready to help — just ask here."
        ).format(period=period_label, amount=amount_label)

    return (
        "📅 Выбран срок подписки: {period}\n"
        "💸 Сумма к оплате: {amount}\n\n"
        "💬 После оплаты вы моментально получите ваш уникальный ключ "
        "подключения к VPN, подробную инструкцию по установке вы можете "
        "найти в главном меню «❓ Как установить?»\n\n"
        "❓ Есть вопрос? Наша служба поддержки готова помочь: просто задайте "
        "его в этом чате."
    ).format(period=period_label, amount=amount_label)
