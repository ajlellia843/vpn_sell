# Contract: bot_service → api_gateway

## Caller / Callee

- **Caller:** bot_service (APIClient in `services/bot_service/app/services/api_client.py`)
- **Callee:** api_gateway (BFF routes under `services/api_gateway/app/routes/bot.py`, prefix `/bot`)
- **Transport:** HTTP, header `X-Service-Key: <api_key>`, timeout 15s

---

## Endpoints and request/response shapes

### POST /bot/me (register or get me)

- **Client method:** `APIClient.get_me(telegram_id, username=None, first_name=None)`
- **Request:** JSON body
  - `telegram_id` (int, required)
  - `username` (str | null, optional)
  - `first_name` (str | null, optional)
- **Response:** 200, JSON object
  - `user`: object (UserRead shape from user_service)
  - `subscription`: object | null (SubscriptionRead shape from billing, or null if none)
- **Required fields in response:** `user` (with `id`, `telegram_id`, etc.), `subscription` (may be null)

---

### GET /bot/me

- **Client method:** not exposed as separate method; bot uses POST /bot/me for registration flow
- **Request:** Query `telegram_id` (int, required)
- **Response:** 200, same shape as POST /bot/me: `{"user": {...}, "subscription": ...}`

---

### GET /bot/plans

- **Client method:** `APIClient.get_plans()`
- **Request:** none (no body, no required query)
- **Response:** 200, JSON array of plan objects (PlanRead-like: id, name, duration_days, price, currency, etc.)

---

### POST /bot/orders

- **Client method:** `APIClient.create_order(telegram_id, plan_id)`
- **Request:** JSON body
  - `telegram_id` (int, required)
  - `plan_id` (str, required, UUID string)
- **Response:** 200, JSON object (OrderRead shape: id, user_id, plan_id, status, amount, currency, payment_url, external_payment_id, created_at, updated_at)

---

### GET /bot/orders/{order_id}

- **Client method:** `APIClient.get_order(order_id)`
- **Request:** path parameter `order_id` (string)
- **Response:** 200, JSON object (OrderRead)

---

### GET /bot/subscription

- **Client method:** `APIClient.get_subscription(telegram_id)`
- **Request:** Query `telegram_id` (int, required)
- **Response:** 200, JSON object
  - `subscription`: object | null (SubscriptionRead or null)
  - `vpn_access`: object | null (VPNAccessRead or null; absent or null if no subscription or VPN not provisioned)

---

### POST /bot/subscription/extend

- **Client method:** `APIClient.extend_subscription(telegram_id, days)`
- **Request:** JSON body
  - `telegram_id` (int, required)
  - `days` (int, required)
- **Response:** 200, JSON object (SubscriptionRead)

---

## Main response statuses

- **200:** Success; body as above.
- **4xx/5xx:** Client raises `APIError(status_code, detail)` with `detail` from response text; no standard error body contract (gateway may return shared `ErrorResponse` from exception handlers).

---

## Main errors (caller side)

- **APIError(status_code, detail):** On HTTP error or request failure. `status_code=0` on network/request errors.
- No shared Pydantic error DTO; bot parses response ad hoc if needed.

---

## Idempotency

- POST /bot/me: Register-or-get is idempotent for same telegram_id (creates or returns existing user).
- POST /bot/orders: Not idempotent; each call creates a new order (billing creates order + YooKassa payment).
- POST /bot/subscription/extend: Not idempotent; extends by N days each time.

---

## Happy path example

**GET /bot/subscription?telegram_id=12345**

1. Bot calls `api_client.get_subscription(12345)`.
2. Gateway returns 200 with `{"subscription": {...}, "vpn_access": {...}}`.
3. Bot uses `subscription` and `vpn_access` for UI.

---

## Error path example

**POST /bot/orders** with invalid plan_id:

1. Gateway gets user, then calls billing create_order; billing returns 404 or 400.
2. Gateway propagates exception, returns 404/400 with error body.
3. APIClient raises `APIError(404, "<response text>")`; bot catches and shows error to user.

---

## Notes

- **needs harmonization:** Response types are plain dicts; no shared Pydantic models on this boundary. Bot uses dict access (e.g. `order.get("payment_url")`). For stub/client testing, formal response DTOs would help.
