"""Formatting helpers for bot messages."""

from __future__ import annotations

_DURATION_LABELS_RU: dict[int, str] = {
    365: "1 год",
    360: "1 год",
    180: "6 месяцев",
    90: "3 месяца",
    30: "1 месяц",
}


def duration_label(days: int, lang: str = "ru") -> str:
    if lang == "ru":
        label = _DURATION_LABELS_RU.get(days)
        if label:
            return label
        if days >= 365:
            return f"{days // 365} г."
        if days >= 30:
            return f"{days // 30} мес."
        return f"{days} дн."
    return f"{days} days"


def format_plan_button(plan: dict) -> str:
    days = plan.get("duration_days", 0)
    price = plan.get("price", "?")
    currency = plan.get("currency", "₽")
    label = duration_label(days)
    return f"🔑 {label}: {price} {currency}"


def format_plan_detail(plan: dict) -> str:
    name = plan.get("name", "—")
    price = plan.get("price", "?")
    currency = plan.get("currency", "₽")
    days = plan.get("duration_days", "?")
    description = plan.get("description", "")
    lines = [
        f"<b>{name}</b>",
        f"Цена: {price} {currency}",
        f"Срок: {duration_label(days) if isinstance(days, int) else days}",
    ]
    if description:
        lines.append(f"\n{description}")
    return "\n".join(lines)


def format_subscription(sub: dict, vpn_access: dict | None = None) -> str:
    status_emoji = "✅" if sub.get("status") == "active" else "⏸"
    lines = [
        f"{status_emoji} <b>Подписка</b>",
        f"Статус: {sub.get('status', '—')}",
        f"Начало: {sub.get('start_at', '—')}",
        f"Окончание: {sub.get('end_at', '—')}",
    ]
    if vpn_access:
        conn_uri = vpn_access.get("connection_uri")
        if conn_uri:
            lines.append(f"\n🔗 <b>Подключение:</b>\n<code>{conn_uri}</code>")
    return "\n".join(lines)


def format_order(order: dict) -> str:
    status_map = {
        "pending": "⏳ Ожидает оплаты",
        "paid": "✅ Оплачен",
        "failed": "❌ Ошибка",
        "cancelled": "❌ Отменён",
    }
    status = order.get("status", "unknown")
    return (
        f"<b>Заказ</b> <code>{order.get('id', '—')}</code>\n"
        f"Статус: {status_map.get(status, status)}\n"
        f"Сумма: {order.get('amount', '?')} {order.get('currency', '₽')}"
    )
