# Current Client Map

Расположение HTTP-клиентов и адаптеров, места создания экземпляров, проброс зависимостей и существующие абстракции.

---

## Расположение клиентов и адаптеров

### Shared (межсервисные клиенты)

| Файл | Класс | Базовый класс | Назначение |
|------|--------|----------------|------------|
| `shared/shared/clients/base.py` | `BaseHTTPClient` | — | Базовый клиент: `httpx.AsyncClient`, ленивое создание, заголовок `X-Service-Key`, tenacity retry, обработка 404/4xx через `NotFoundError`/`ServiceError`. Методы `get`, `post`, `put`, `patch`, `delete` возвращают `dict[str, Any]`. |
| `shared/shared/clients/user.py` | `UserServiceClient` | `BaseHTTPClient` | `/users/` (register_or_get), `/users/{id}`, `/users/by-telegram/{id}`, `/users/` list, PATCH user. |
| `shared/shared/clients/billing.py` | `BillingServiceClient` | `BaseHTTPClient` | Планы, заказы, подписки: `/plans/`, `/orders/`, `/subscriptions/`, `/subscriptions/user/{id}/active`, extend, revoke. |
| `shared/shared/clients/vpn.py` | `VPNServiceClient` | `BaseHTTPClient` | `provision`, `extend`, `disable`, `enable`, `get_access` — пути без префикса (см. раздел Inconsistency ниже). |

### Bot → api_gateway

| Файл | Класс | Базовый класс | Назначение |
|------|--------|----------------|------------|
| `services/bot_service/app/services/api_client.py` | `APIClient` | нет (свой `httpx.AsyncClient`) | Вызовы `/bot/me`, `/bot/plans`, `/bot/orders`, `/bot/subscription`, extend. Собственный тип ошибки `APIError`. Без retry, без общего базового клиента из shared. |

### Внешние API (не между нашими сервисами)

| Файл | Класс/функция | Назначение |
|------|----------------|------------|
| `services/vpn_service/app/adapters/base.py` | `AbstractVPNPanelAdapter` | Абстрактный интерфейс панели: `authenticate`, `create_client`, `get_client`, `extend_client`, `disable_client`, `enable_client`, `get_client_link`, `inbound_id`. |
| `services/vpn_service/app/adapters/xui.py` | `XUIAdapter` | Реализация под 3x-ui: httpx, логин, работа с клиентами и трафиком. |
| `services/billing_service/app/services/yookassa.py` | `YooKassaService` | Создание платежа и верификация webhook; внутри используется `async with httpx.AsyncClient()` для разового POST. |

### Разовые HTTP-вызовы (без класса-клиента в state)

| Файл | Место | Описание |
|------|--------|----------|
| `services/api_gateway/app/routes/webhooks.py` | `yookassa_webhook` | `async with httpx.AsyncClient(timeout=15.0)` — пересылка тела запроса в billing `/webhooks/yookassa`. Заголовки не добавляются (в т.ч. X-Service-Key не нужен для webhooks в billing). |

---

## Где создаются экземпляры клиентов

| Сервис | Файл | Где создаётся | Что кладётся в state |
|--------|------|----------------|----------------------|
| api_gateway | `app/main.py` | В `lifespan(application)` до `yield` | `user_client`, `billing_client`, `vpn_client`, `billing_service_url`. При shutdown — `close()` у всех трёх клиентов. |
| admin_service | `app/main.py` | В `lifespan(_app)` после создания схемы БД | `user_client`, `billing_client`, `vpn_client`. При shutdown — закрытие клиентов и db. |
| billing_service | `app/main.py` | В `lifespan(_app)` после `db.create_schema()` | `db`, `vpn_client` (VPNServiceClient), `yookassa` (YooKassaService). При shutdown — закрытие vpn_client и db. |
| bot_service | `app/main.py` | На уровне модуля (до lifespan) | Глобальный `api_client = APIClient(...)`, затем `dp["api_client"] = api_client`. В lifespan webhook-приложения — только `set_webhook`/`delete_webhook` и `await api_client.close()` при выходе. |
| vpn_service | `app/main.py` | В `lifespan(app)` внутри `create_app()` | `vpn_adapter` (экземпляр XUIAdapter), после `authenticate()`. Не HTTP-клиент к другому нашему сервису. |
| user_service | — | — | Не создаёт клиентов к другим сервисам. |

---

## Как пробрасываются зависимости

- **api_gateway:** Роуты в `app/routes/bot.py` получают клиентов через хелперы `_user_client(request)`, `_billing_client(request)`, `_vpn_client(request)`, которые возвращают `request.app.state.*_client`. Явного FastAPI `Depends` для клиентов нет.
- **admin_service:** В роутах напрямую: `request.app.state.user_client`, `request.app.state.billing_client`. `vpn_client` в state есть, но в коде роутов не используется.
- **billing_service:** В каждом роуте, где нужен billing-оркестратор, создаётся `BillingService(session=..., yookassa=request.app.state.yookassa, vpn_client=request.app.state.vpn_client)`. Сессия БД — через `Depends(get_session)` из `app/dependencies.py`.
- **bot_service:** Хендлеры получают клиент из контекста aiogram: `dp["api_client"]` (устанавливается в main). В коде часто через инъекцию или доступ к контексту (зависит от хендлера).
- **vpn_service:** В `app/routes/vpn.py` сервис провизионирования собирается как `_build_service(session, request)` → `ProvisioningService(session, request.app.state.vpn_adapter)`. Сессия — через кастомный `_get_session(request)`.

---

## Абстракции, которые можно расширить

1. **`BaseHTTPClient` (shared)**  
   Единая точка для retry, заголовка `X-Service-Key`, обработки ошибок. Все три shared-клиента (user, billing, vpn) наследуются от него. Для нового внутреннего сервиса можно добавить наследника в `shared/shared/clients/` и подключать в gateway/admin/billing по тому же паттерну (lifespan + app.state).

2. **`AbstractVPNPanelAdapter` (vpn_service)**  
   Позволяет подменить реализацию панели (сейчас только XUIAdapter). Добавление другой панели = новая реализация адаптера и выбор в конфиге/lifespan, без ломки ProvisioningService.

3. **Единого интерфейса/протокола для «сервисных клиентов» в api_gateway/admin/billing нет** — используются конкретные классы из shared. При желании ввести общий контракт (например, для тестов или подмены) потребуется введение абстракций на стороне вызывающих сервисов.

4. **bot_service APIClient** не наследует `BaseHTTPClient`, не использует shared-схемы. Унификация с shared (если нужна) — отдельная точка расширения: либо перенос в shared, либо введение общего базового класса и типизированных DTO на границе bot ↔ gateway.

---

## Inconsistency: пути VPN-клиента и роутов vpn_service

В **`shared/shared/clients/vpn.py`** методы вызывают:

- `POST /provision`
- `POST /extend`
- `POST /disable`
- `POST /enable`
- `GET /access/{subscription_id}`

В **vpn_service** роутер объявлен с префиксом:

- `router = APIRouter(prefix="/vpn", tags=["vpn"])` в `services/vpn_service/app/routes/vpn.py`

Итоговые пути приложения: **`/vpn/provision`**, **`/vpn/extend`**, **`/vpn/disable`**, **`/vpn/enable`**, **`/vpn/access/{subscription_id}`**.

Если `base_url` при создании `VPNServiceClient` задаётся как корень сервиса (например, `http://vpn-service:8000`), то клиент обращается к `http://vpn-service:8000/provision` и т.д., что даёт **404**, так как реальный путь — `http://vpn-service:8000/vpn/provision`.

**Варианты согласования (без изменения логики в этом документе):**

- В конфигурации сервисов, вызывающих vpn_service (api_gateway, billing_service, admin_service), задавать `vpn_service_url` с суффиксом `/vpn`, например `http://vpn-service:8000/vpn`; либо
- Изменить пути в `VPNServiceClient`, чтобы они включали префикс `/vpn`.

Текущее состояние в коде — несоответствие путей и риск 404 при вызовах к vpn_service.
