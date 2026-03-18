# Stub architecture: protocol + real/stub + provider

Краткое описание того, где лежат протоколы, реальные и стаб-клиенты, как выбирается реализация и как масштабировать на остальные сервисы.

---

## Где лежат protocols (интерфейсы)

- **shared/shared/protocols/**  
  - `gateway.py` — ApiGatewayClientProtocol (bot → api_gateway)  
  - `user.py` — UserServiceClientProtocol  
  - `billing.py` — BillingServiceClientProtocol  
  - `vpn.py` — VPNServiceClientProtocol  
  - `payment.py` — PaymentProviderProtocol (YooKassa)  
- **vpn_service:** интерфейс панели уже есть — `app/adapters/base.py` (AbstractVPNPanelAdapter). Отдельный протокол в shared для XUI не вводился.

---

## Где лежат real clients

- **shared/shared/clients/** — UserServiceClient, BillingServiceClient, VPNServiceClient (наследуют BaseHTTPClient).  
- **bot_service:** `app/services/api_client.py` — APIClient (реальный клиент к api_gateway).  
- **billing_service:** `app/services/yookassa.py` — YooKassaService.  
- **vpn_service:** `app/adapters/xui.py` — XUIAdapter (реальная панель 3x-ui).

Реализации не обязаны явно наследовать протоколы (в Python Protocol — структурная типизация); достаточно совпадения методов.

---

## Где лежат stub clients

- **shared/shared/stubs/**  
  - `gateway.py` — StubApiGatewayClient  
  - `user.py` — StubUserServiceClient  
  - `billing.py` — StubBillingServiceClient  
  - `vpn.py` — StubVPNServiceClient  
  - `yookassa.py` — StubYooKassaService  
- **shared/shared/stubs/fixtures.py** — общие фикстурные данные (STUB_USER_ID, stub_user(), stub_plan(), и т.д.).  
- **vpn_service:** `app/adapters/stub_xui.py` — StubXUIAdapter (реализует AbstractVPNPanelAdapter).

Стабы возвращают минимальные данные из fixtures или константы; HTTP не вызывают.

---

## Где происходит выбор реализации

Выбор **real vs stub** делается **только в провайдерах** по флагам из settings:

| Сервис        | Файл провайдеров           | Флаги (env) |
|---------------|----------------------------|-------------|
| bot_service   | app/providers.py           | USE_STUB_API_GATEWAY |
| api_gateway   | app/providers.py           | USE_STUB_USER_SERVICE, USE_STUB_BILLING_SERVICE, USE_STUB_VPN_SERVICE |
| billing_service | app/providers.py         | USE_STUB_VPN_SERVICE, USE_STUB_YOOKASSA |
| admin_service | app/providers.py           | USE_STUB_USER_SERVICE, USE_STUB_BILLING_SERVICE, USE_STUB_VPN_SERVICE |
| vpn_service   | app/providers.py           | USE_STUB_XUI |

В коде используется **snake_case**: `use_stub_api_gateway`, `use_stub_user_service` и т.д. В `.env` — `USE_STUB_API_GATEWAY`, `USE_STUB_USER_SERVICE` и т.д. (pydantic-settings по умолчанию берёт переменные окружения в верхнем регистре).

Роуты, хендлеры и доменная логика **не проверяют** флаги и не знают, real это клиент или stub; они получают готовый экземпляр из `app.state` или из фабрики при старте.

---

## Как включить stub mode

В `.env` соответствующего сервиса (или в переменных окружения при запуске):

```bash
# bot_service
USE_STUB_API_GATEWAY=true

# api_gateway
USE_STUB_USER_SERVICE=true
USE_STUB_BILLING_SERVICE=true
USE_STUB_VPN_SERVICE=true

# billing_service
USE_STUB_VPN_SERVICE=true
USE_STUB_YOOKASSA=true

# admin_service
USE_STUB_USER_SERVICE=true
USE_STUB_BILLING_SERVICE=true
USE_STUB_VPN_SERVICE=true

# vpn_service
USE_STUB_XUI=true
```

По умолчанию все флаги `false` — используются реальные клиенты/адаптеры.

---

## Масштабирование на остальные сервисы

1. **Новый зависимый клиент (например, ещё один внутренний сервис):**  
   - Добавить протокол в `shared/shared/protocols/`.  
   - Реализацию оставить в `shared/clients/` или в сервисе.  
   - Добавить стаб в `shared/shared/stubs/`.  
   - В сервисе-потребителе: флаг `use_stub_<name>` в config, функция в `app/providers.py`, в lifespan подставлять результат провайдера в `app.state`.

2. **Новый внешний адаптер (как 3x-ui):**  
   - Интерфейс в самом сервисе (как AbstractVPNPanelAdapter).  
   - Реальная реализация и стаб (как XUIAdapter и StubXUIAdapter).  
   - В `app/providers.py` этого сервиса — выбор по флагу и возврат одного из адаптеров.

3. **Единый стиль:**  
   - Выбор real/stub только в провайдерах.  
   - Бизнес-логика и роуты не зависят от типа реализации.
