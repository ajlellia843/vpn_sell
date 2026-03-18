# User Stub Flow: reference implementation

Эталонная реализация паттерна protocol + real/stub на домене user_service.

---

## Как включить stub

В `.env` нужного сервиса (или env-переменной при запуске):

```bash
# api_gateway: user_service заменяется стабом
USE_STUB_USER_SERVICE=true

# admin_service: то же самое
USE_STUB_USER_SERVICE=true

# bot_service: stub для всего api_gateway (включая user flow внутри)
USE_STUB_API_GATEWAY=true
```

По умолчанию все `false` -- используются реальные клиенты.

---

## Какой запрос проходит через цепочку

### Сценарий: /start в Telegram

```
User (Telegram)
  │
  ▼
bot_service  (handler start.py)
  │ api_client.get_me(telegram_id, username, first_name)
  ▼
api_gateway  (routes/bot.py → POST /bot/me)
  │ _user_client(request).register_or_get(telegram_id, username, first_name)
  ▼
user_service  (routes/user.py → POST /users/)
  │ UserService.register_or_get
  ▼
Response: UserRead JSON
```

В stub mode:

```
bot_service  ──► StubApiGatewayClient.get_me()
                  └─► StubUserServiceClient.register_or_get()
                       └─► возвращает fixture dict

api_gateway  ──► StubUserServiceClient.register_or_get()
                  └─► возвращает fixture dict (UserRead-совместимый)
```

Бизнес-логика не знает, что работает stub: ни хендлеры бота, ни роуты gateway не содержат if/else для stub.

---

## Какой ответ ожидается

### register_or_get (known telegram_id = 12345)

```json
{
  "id": "a0000000-0000-0000-0000-000000000001",
  "telegram_id": 12345,
  "username": "stub_user",
  "first_name": "Stub",
  "is_active": true,
  "created_at": "2026-03-18T...",
  "updated_at": "2026-03-18T..."
}
```

Совпадает со структурой `shared.schemas.user.UserRead`.

### register_or_get (unknown telegram_id)

Создаёт нового пользователя (новый UUID), возвращает аналогичную структуру.

### get_by_telegram_id (unknown telegram_id = 99999999)

Raises `shared.exceptions.NotFoundError("User with telegram_id=99999999 not found")` -- то же поведение, что и реальный user_service.

---

## Какие сценарии покрыты

| Сценарий | Метод | Поведение stub | Тест |
|----------|-------|----------------|------|
| Регистрация нового пользователя | `register_or_get(unknown_tg)` | Создаёт пользователя в in-memory store, возвращает UserRead-like dict | `test_register_or_get_new` |
| Получение существующего пользователя | `register_or_get(known_tg)` | Возвращает существующий без создания нового | `test_register_or_get_existing` |
| Поиск по telegram_id (найден) | `get_by_telegram_id(known_tg)` | Возвращает UserRead-like dict | `test_get_by_telegram_id_found` |
| Поиск по telegram_id (не найден) | `get_by_telegram_id(unknown_tg)` | Raises NotFoundError | `test_get_by_telegram_id_not_found` |
| Получение по user_id (найден) | `get_user(known_id)` | Возвращает UserRead-like dict | `test_get_user_found` |
| Получение по user_id (не найден) | `get_user(unknown_id)` | Raises NotFoundError | `test_get_user_not_found` |
| Список пользователей | `list_users(offset, limit)` | Возвращает `{items: [...], total: N}` с пагинацией | `test_list_users` |
| Обновление пользователя | `update_user(id, **kwargs)` | Возвращает обновлённый dict | `test_update_user` |
| Обновление (не найден) | `update_user(unknown_id, ...)` | Raises NotFoundError | `test_update_user_not_found` |
| Bot: get_me (known) | `StubApiGatewayClient.get_me()` | `{user: ..., subscription: ...}` | `test_get_me_known_user` |
| Bot: get_me (new) | `StubApiGatewayClient.get_me(new_tg)` | Регистрирует и возвращает | `test_get_me_new_user` |
| Bot: get_subscription (unknown) | `StubApiGatewayClient.get_subscription(unknown_tg)` | Raises NotFoundError | `test_get_subscription_unknown_user` |
| Bot: create_order (unknown user) | `StubApiGatewayClient.create_order(unknown_tg, plan)` | Raises NotFoundError | `test_create_order_unknown_user` |

Тесты: `tests/test_user_stub_chain.py` (15 тестов, все проходят).

---

## Как запустить тесты

```bash
cd vpn_sell
PYTHONPATH=shared pytest tests/test_user_stub_chain.py -v
```

---

## Структура эталонных файлов

```
shared/shared/
  protocols/
    user.py         ← UserServiceClientProtocol
    gateway.py      ← ApiGatewayClientProtocol
  stubs/
    fixtures.py     ← shared fixture data + known IDs
    user.py         ← StubUserServiceClient (in-memory store, NotFoundError)
    gateway.py      ← StubApiGatewayClient (composes StubUserServiceClient)
  clients/
    user.py         ← UserServiceClient (real HTTP client, unchanged)

services/api_gateway/app/
  providers.py      ← provide_user_client(settings) → real or stub
  routes/bot.py     ← type hints: UserServiceClientProtocol (не конкретный класс)

services/bot_service/app/
  providers.py      ← provide_gateway_client(settings) → real or stub

services/admin_service/app/
  providers.py      ← provide_user_client(settings) → real or stub

tests/
  test_user_stub_chain.py  ← 15 smoke tests
```

---

## Как распространить на billing / vpn

Тот же шаблон:

1. Протокол уже есть: `shared/shared/protocols/billing.py`, `vpn.py`, `payment.py`.
2. Стаб уже есть (каркас): `shared/shared/stubs/billing.py`, `vpn.py`, `yookassa.py`.
3. Нужно: добавить in-memory store и NotFoundError сценарии (как сделано для user); добавить тесты; убедиться, что фикстуры совместимы с реальными DTO (OrderRead, SubscriptionRead, PlanRead, ProvisionResponse).
4. Провайдеры (`providers.py`) и конфиг-флаги уже готовы для всех сервисов.
