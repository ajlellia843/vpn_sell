"""Texts for referral and partner programs."""

from __future__ import annotations


def partner_program_text(
    link: str,
    transitions: int,
    purchases: int,
    profit: str,
    available: str,
    conversion: str,
    lang: str = "ru",
) -> str:
    """Return the partner program text with stats."""
    if lang == "en":
        return (
            "💼 <b>Partner program</b>\n\n"
            "💰 Invite friends and earn up to 30% from their purchases and top-ups, "
            "forever!\n\n"
            "🔗 Your partner link:\n"
            "{link}\n\n"
            "🏆 <b>Stats:</b>\n"
            "├ Link clicks: {transitions}\n"
            "├ Purchases: {purchases}\n"
            "├ Profit: {profit}\n"
            "├ Available to withdraw: {available}\n"
            "└ Conversion to purchases: {conversion}"
        ).format(
            link=link,
            transitions=transitions,
            purchases=purchases,
            profit=profit,
            available=available,
            conversion=conversion,
        )

    return (
        "💼 <b>Партнерская программа</b>\n\n"
        "💰 Приводи друзей и зарабатывай до 30% с их покупок и пополнений, "
        "пожизненно!\n\n"
        "🔗 Ваша партнерская ссылка:\n"
        "{link}\n\n"
        "🏆 <b>Статистика:</b>\n"
        "├ Переходов по ссылке: {transitions}\n"
        "├ Покупок: {purchases}\n"
        "├ Прибыль: {profit}\n"
        "├ Доступно для вывода: {available}\n"
        "└ Конверсия в покупки: {conversion}"
    ).format(
        link=link,
        transitions=transitions,
        purchases=purchases,
        profit=profit,
        available=available,
        conversion=conversion,
    )


def referral_program_text(
    link: str,
    invited: int,
    paid: int,
    available_months: str,
    lang: str = "ru",
) -> str:
    """Return the referral program text with stats."""
    if lang == "en":
        return (
            "🤝 <b>Referral program</b>\n\n"
            "🔥 Get a subscription by inviting friends via your referral link. "
            "If they subscribe, we will gift you one month of NashVPN for each.\n\n"
            # "💰 If you are a blogger or run a large community, join our partner "
            # "program and earn up to 30% from their purchases and top-ups, forever!\n\n"
            "🔗 Your referral link:\n"
            "{link}\n\n"
            "🏆 <b>Stats:</b>\n"
            "├ Friends invited: {invited}\n"
            "├ Friends who paid: {paid}\n"
            "└ Available to extend: {available_months}"
        ).format(
            link=link,
            invited=invited,
            paid=paid,
            available_months=available_months,
        )

    return (
        "🤝 <b>Реферальная программа</b>\n\n"
        "🔥 Получите подписку, пригласив друзей по реферальной ссылке. Если "
        "после этого они оформят подписку, мы подарим вам за каждого по одному "
        "месяцу подписки на NashVPN!\n\n"
        # "💰 А если вы блогер или владелец крупного сообщества, присоединяйтесь "
        # "к нашей партнерской программе и зарабатывайте до 30% с их покупок и "
        # "пополнений, пожизненно!\n\n"
        "🔗 Ваша реферальная ссылка:\n"
        "{link}\n\n"
        "🏆 <b>Статистика:</b>\n"
        "├ Приведено друзей: {invited}\n"
        "├ Друзей, оплативших VPN: {paid}\n"
        "└ Доступно для продления: {available_months}"
    ).format(
        link=link,
        invited=invited,
        paid=paid,
        available_months=available_months,
    )
