# Contract: api_gateway → billing_service

## Caller / Callee

- **Caller:** api_gateway (via `BillingServiceClient` from shared, used in `services/api_gateway/app/routes/bot.py`)
- **Callee:** billing_service (routes in `services/billing_service/app/routes/` — plan, order, subscription; prefixes `/plans`, `/orders`, `/subscriptions`)
- **Transport:** HTTP, header `X-Service-Key: <service_api_key>`, shared `BaseHTTPClient`

---

## Endpoints used by api_gateway

### GET /plans/

- **Gateway usage:** `_billing_client(request).list_plans()`
- **Request:** none
- **Response:** 200, JSON array of `PlanRead`: id, name, duration_days, price, currency, description, traffic_limit_gb, device_limit, is_active, created_at
- **Required fields (per item):** id, name, duration_days, price, currency, device_limit, is_active, created_at

---

### GET /subscriptions/user/{user_id}/active

- **Gateway usage:** `_billing_client(request).get_active_subscription(user_id)` — passes `user["id"]` (string/UUID)
- **Request:** path `user_id` (UUID)
- **Response:** 200 with `SubscriptionRead` or 404; client catches exception and returns **None** on error (no exception to gateway)
- **Response shape when 200:** id, user_id, plan_id, order_id, start_at, end_at, status, auto_provisioned, created_at
- **Note:** Client returns `None` on any exception for this call, so gateway receives either subscription object or null.

---

### POST /orders/

- **Gateway usage:** `_billing_client(request).create_order(user["id"], body.plan_id)` — user_id and plan_id as strings
- **Request:** JSON `OrderCreate`: `user_id` (UUID), `plan_id` (UUID)
- **Response:** 201, `OrderRead`: id, user_id, plan_id, status, amount, currency, payment_url, external_payment_id, provider_payload, created_at, updated_at
- **Required response fields:** id, user_id, plan_id, status, payment_url (after YooKassa creation), amount, currency, created_at, updated_at

---

### GET /orders/{order_id}

- **Gateway usage:** `_billing_client(request).get_order(order_id)`
- **Request:** path `order_id` (UUID)
- **Response:** 200, OrderRead
- **Errors:** 404 if order not found

---

### POST /subscriptions/{sub_id}/extend

- **Gateway usage:** `_billing_client(request).extend_subscription(subscription["id"], body.days)`
- **Request:** path `sub_id` (UUID), JSON body `{"days": int}`
- **Response:** 200, SubscriptionRead
- **Errors:** 404 if subscription not found

---

## Main response statuses

- **200/201:** Success.
- **404:** NotFoundError (order, subscription, plan); body `{"error": {"code": "NOT_FOUND", "message": "..."}}`.
- **4xx/5xx:** ServiceError; body with `error.code`, `error.message`, `error.details`.

---

## Main errors (caller side)

- `NotFoundError` on 404 (except get_active_subscription, which swallows and returns None).
- `ServiceError` on other HTTP errors.
- Billing may raise `NotFoundError` for invalid plan (create_order), inactive plan, etc.

---

## Idempotency

- GET /plans/, GET /orders/{id}, GET /subscriptions/user/{id}/active: Idempotent.
- POST /orders/: Not idempotent; each call creates new order and YooKassa payment.
- POST /subscriptions/{id}/extend: Not idempotent; adds days each time.

---

## Happy path example

Create order for user and plan:

1. Gateway has user from user_service; calls `billing_client.create_order(user["id"], plan_id)`.
2. Billing creates order, calls YooKassa, returns 201 with OrderRead (includes payment_url).
3. Gateway returns that object to bot; bot redirects user to payment_url.

---

## Error path example

Plan not found or inactive:

1. POST /orders/ with invalid plan_id → billing raises NotFoundError → 404.
2. BaseHTTPClient raises NotFoundError to gateway.
3. Gateway propagates to bot; bot gets APIError(404, ...).

---

## Notes

- Contract is stable: billing_service uses shared schemas PlanRead, OrderRead, OrderRead, SubscriptionRead; gateway uses same client and expects matching JSON. get_active_subscription returning None on error is a deliberate client-level behavior (no exception to gateway).
