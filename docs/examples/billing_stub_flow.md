# Billing Stub Flow — Reference Implementation

## Как включить

Billing-стаб активируется через env-переменные (или `.env`) в сервисах-потребителях.
Сам `billing_service` при этом **не запускается** — все ответы формируются in-memory.

### api_gateway

```env
USE_STUB_BILLING_SERVICE=true
```

### admin_service

```env
USE_STUB_BILLING_SERVICE=true
```

### bot_service (через gateway stub)

```env
USE_STUB_API_GATEWAY=true
```

> Когда `bot_service` работает со `StubApiGatewayClient`, billing-сценарии
> автоматически обслуживаются внутренним `StubBillingServiceClient`.

---

## Архитектура стаба

```
StubBillingServiceClient (shared/shared/stubs/billing.py)
├── in-memory store: _plans, _orders, _subscriptions
├── seeded from fixtures: stub_plan(), stub_order(), stub_subscription(), etc.
├── NotFoundError для отсутствующих сущностей
└── реалистичные мутации (extend_subscription, revoke_subscription, create_order)

StubApiGatewayClient (shared/shared/stubs/gateway.py)
├── composes StubUserServiceClient + StubBillingServiceClient
├── реплицирует логику api_gateway/routes/bot.py
└── пропагирует ошибки (NotFoundError) от внутренних стабов
```

---

## Поддерживаемые сценарии

### Plans

| Сценарий | Метод | Поведение |
|---|---|---|
| Список активных планов | `list_plans()` | 2 плана (30d, 90d), только `is_active=True` |
| Получение плана по ID | `get_plan(id)` | Возвращает план; `NotFoundError` если нет |
| Создание плана | `create_plan(data)` | Добавляет в store, возвращает `PlanRead`-compatible dict |
| Обновление плана | `update_plan(id, data)` | Мутирует in-place; `NotFoundError` если нет |

### Orders

| Сценарий | Метод | Поведение |
|---|---|---|
| Создание заказа | `create_order(user_id, plan_id)` | Проверяет план (active); возвращает `OrderRead`-compatible dict с `payment_url` |
| Создание заказа (план не найден) | `create_order(user_id, bad_id)` | `NotFoundError` |
| Создание заказа (неактивный план) | `create_order(user_id, inactive_id)` | `NotFoundError` |
| Получение заказа | `get_order(id)` | Возвращает заказ; `NotFoundError` если нет |
| Список заказов (pagination) | `list_orders(offset, limit, status)` | `{"items": [...], "total": N}` |
| Список заказов пользователя | `list_orders_by_user(user_id)` | Фильтр по `user_id` |

### Subscriptions

| Сценарий | Метод | Поведение |
|---|---|---|
| Активная подписка | `get_active_subscription(user_id)` | Возвращает подписку или `None` |
| Нет активной подписки | `get_active_subscription(unknown_user_id)` | `None` |
| Подписка по ID | `get_subscription(id)` | Возвращает; `NotFoundError` если нет |
| Продление | `extend_subscription(id, days)` | Мутирует `end_at`; `NotFoundError` если нет |
| Отзыв | `revoke_subscription(id)` | Ставит `status="cancelled"`; `NotFoundError` если нет |
| Список (pagination) | `list_subscriptions(offset, limit, status)` | `{"items": [...], "total": N}` |

---

## Примеры потоков

### 1. bot `/start` → get_me (через gateway stub)

```
bot_service -> StubApiGatewayClient.get_me(telegram_id=12345)
  └─ StubUserServiceClient.register_or_get(12345)  → user dict
  └─ StubBillingServiceClient.get_active_subscription(user_id)  → subscription dict
  → {"user": {...}, "subscription": {...}}
```

### 2. bot «Оформить подписку» → create_order

```
bot_service -> StubApiGatewayClient.create_order(telegram_id=12345, plan_id="b000...")
  └─ StubUserServiceClient.get_by_telegram_id(12345)  → user dict
  └─ StubBillingServiceClient.create_order(user_id, plan_id)  → order dict
  → {"id": "...", "status": "pending", "payment_url": "https://stub.example/pay", ...}
```

### 3. admin «Продлить подписку»

```
admin_service -> StubBillingServiceClient.extend_subscription(sub_id, 30)
  → end_at увеличен на 30 дней
```

### 4. api_gateway «Продлить подписку» (bot flow)

```
api_gateway -> StubBillingServiceClient.get_active_subscription(user_id)  → sub
api_gateway -> StubBillingServiceClient.extend_subscription(sub["id"], 15)
  → SubscriptionRead-compatible dict с обновлённым end_at
```

---

## DTO-совместимость

Все stub-ответы проходят валидацию через реальные Pydantic-схемы:

- `PlanRead.model_validate(stub_response)` — OK
- `OrderRead.model_validate(stub_response)` — OK
- `SubscriptionRead.model_validate(stub_response)` — OK

Тесты: `tests/test_billing_stub_chain.py` (31 тест).

---

## Стабильные fixture-идентификаторы

| Константа | Значение | Назначение |
|---|---|---|
| `STUB_PLAN_ID` | `b0000000-...-01` | Активный план 30d |
| `STUB_PLAN_ID_2` | `b0000000-...-02` | Активный план 90d |
| `STUB_PLAN_ID_INACTIVE` | `b0000000-...-99` | Неактивный план |
| `STUB_ORDER_ID` | `c0000000-...-01` | Pending заказ |
| `STUB_ORDER_ID_PAID` | `c0000000-...-02` | Оплаченный заказ |
| `STUB_SUBSCRIPTION_ID` | `d0000000-...-01` | Активная подписка |
| `STUB_SUBSCRIPTION_ID_EXPIRED` | `d0000000-...-99` | Просроченная подписка |
| `STUB_USER_ID_NO_SUB` | `a0000000-...-99` | Пользователь без подписки |

---

## Файловая структура

```
shared/shared/
├── compat.py                         # StrEnum shim для Python < 3.11
├── stubs/
│   ├── __init__.py                   # re-exports
│   ├── fixtures.py                   # Stable test data factories
│   ├── billing.py                    # StubBillingServiceClient (in-memory)
│   ├── gateway.py                    # StubApiGatewayClient (composes user + billing)
│   ├── user.py                       # StubUserServiceClient
│   ├── vpn.py                        # StubVPNServiceClient (каркас)
│   └── yookassa.py                   # StubYooKassaService (каркас)
├── protocols/
│   └── billing.py                    # BillingServiceClientProtocol
services/api_gateway/app/
├── providers.py                      # provide_billing_client() → real | stub
├── config.py                         # use_stub_billing_service flag
services/admin_service/app/
├── providers.py                      # provide_billing_client() → real | stub
├── config.py                         # use_stub_billing_service flag
tests/
└── test_billing_stub_chain.py        # 31 smoke test
```

---

## Что ещё завязано на реальные зависимости

| Компонент | Зависимость | Статус |
|---|---|---|
| `billing_service` внутренний `BillingService` | PostgreSQL (orders, plans, subscriptions) | Не стабится (internal domain logic) |
| `billing_service` → `YooKassa` | Внешний платёжный провайдер | `StubYooKassaService` — каркас, требует доработки |
| `billing_service` → `vpn_service` | Провижинг VPN при оплате | `StubVPNServiceClient` — каркас |
| Webhook `/payment/callback` | YooKassa callback | Не покрыт стабом |
