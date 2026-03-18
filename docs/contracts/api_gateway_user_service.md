# Contract: api_gateway → user_service

## Caller / Callee

- **Caller:** api_gateway (via `UserServiceClient` from shared, used in `services/api_gateway/app/routes/bot.py`)
- **Callee:** user_service (routes in `services/user_service/app/routes/user.py`, prefix `/users`)
- **Transport:** HTTP, header `X-Service-Key: <service_api_key>`, shared `BaseHTTPClient` (retry, timeout 10s)

---

## Endpoints and request/response shapes

### POST /users/ (register or get)

- **Gateway usage:** `_user_client(request).register_or_get(telegram_id, username, first_name)`
- **Request:** JSON body — `UserCreate`: `telegram_id` (int), `username` (str | null), `first_name` (str | null)
- **Response:** 200, `UserRead`: `id` (UUID), `telegram_id`, `username`, `first_name`, `is_active`, `created_at`, `updated_at`
- **Required response fields:** id, telegram_id, is_active, created_at, updated_at

---

### GET /users/by-telegram/{telegram_id}

- **Gateway usage:** `_user_client(request).get_by_telegram_id(telegram_id)`
- **Request:** path `telegram_id` (int)
- **Response:** 200, `UserRead` (same as above)
- **Errors:** 404 NotFoundError if user not found

---

### GET /users/ (list)

- **Gateway usage:** not used by api_gateway bot routes; used by admin_service
- **Request:** query `offset` (int, default 0), `limit` (int, default 50)
- **Response:** 200, `{"items": [UserRead, ...], "total": int}`

---

### GET /users/{user_id}

- **Gateway usage:** not used in current gateway bot routes
- **Request:** path `user_id` (UUID)
- **Response:** 200, UserRead

---

### PATCH /users/{user_id}

- **Gateway usage:** not used in current gateway bot routes
- **Request:** path `user_id`, JSON body (partial UserUpdate)
- **Response:** 200, UserRead

---

## Main response statuses

- **200:** Success.
- **404:** User not found (get_by_telegram_id, get_user); shared `ErrorResponse`: `{"error": {"code": "NOT_FOUND", "message": "..."}}`.
- **4xx/5xx:** ServiceError-style body with `error.code`, `error.message`, `error.details`.

---

## Main errors (caller side)

- `NotFoundError(message)` from shared (BaseHTTPClient raises on 404).
- `ServiceError(message)` on other 4xx/5xx.
- Response body: `ErrorResponse` with `error: { code, message, details }`.

---

## Idempotency

- POST /users/ (register_or_get): Idempotent for same telegram_id; returns existing user if present.

---

## Happy path example

Gateway needs user for telegram_id 12345:

1. Call `user_client.get_by_telegram_id(12345)`.
2. user_service returns 200 with UserRead JSON.
3. Gateway uses `user["id"]` for billing calls.

---

## Error path example

User not found:

1. GET /users/by-telegram/999999 → 404, body `{"error": {"code": "NOT_FOUND", "message": "..."}}`.
2. UserServiceClient (BaseHTTPClient) raises `NotFoundError(message)`.
3. Gateway may propagate to bot as 404.

---

## Notes

- Contract is stable: user_service uses shared schemas `UserCreate`, `UserRead`, `UserUpdate`; gateway receives JSON that matches UserRead. No inconsistency on this boundary.
