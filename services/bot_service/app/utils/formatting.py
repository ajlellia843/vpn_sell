from __future__ import annotations


def format_plan(plan: dict) -> str:
    name = plan.get("name", "—")
    price = plan.get("price", "?")
    currency = plan.get("currency", "₽")
    days = plan.get("duration_days", "?")
    description = plan.get("description", "")
    lines = [
        f"<b>{name}</b>",
        f"Цена: {price} {currency}",
        f"Срок: {days} дней",
    ]
    if description:
        lines.append(f"\n{description}")
    return "\n".join(lines)


def format_subscription(sub: dict, vpn_access: dict | None = None) -> str:
    status_emoji = "✅" if sub.get("status") == "active" else "⏸"
    lines = [
        f"{status_emoji} <b>Подписка</b>",
        f"Статус: {sub.get('status', '—')}",
        f"Начало: {sub.get('start_date', '—')}",
        f"Окончание: {sub.get('end_date', '—')}",
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
