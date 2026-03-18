# Contract: billing_service → YooKassa

## Caller / Callee

- **Caller:** billing_service (`YooKassaService` in `services/billing_service/app/services/yookassa.py`)
- **Callee:** YooKassa API (external), base URL `https://api.yookassa.ru/v3`
- **Transport:** HTTP, Basic Auth (shop_id, secret_key), one-off `httpx.AsyncClient()` per create_payment call; no shared client instance

---

## Outgoing: create payment

### POST https://api.yookassa.ru/v3/payments

- **Caller usage:** `BillingService.create_order` → `_yookassa.create_payment(order_id, amount, currency, description)`
- **Request:**
  - Headers: `Idempotence-Key: <new UUID per call>` (YooKassa idempotency)
  - JSON: amount (value as string, currency), confirmation (type "redirect", return_url), capture true, description, metadata.order_id
- **Request shape (essential):**
  - `amount`: `{"value": "<decimal string>", "currency": "RUB"}`
  - `confirmation`: `{"type": "redirect", "return_url": "<return_url from config>"}`
  - `capture`: true
  - `description`: string
  - `metadata`: `{"order_id": "<order_id>"}`
- **Response (success):** 200, YooKassa payment object; caller uses:
  - `data["id"]` → payment_id
  - `data["confirmation"]["confirmation_url"]` → confirmation_url
- **Returned to billing:** `{"payment_id": "...", "confirmation_url": "..."}` (dict[str, str])
- **Errors:** resp.raise_for_status() — HTTP errors propagate; no custom error mapping in code.

---

## Incoming: webhook notification

- **Entry:** YooKassa sends POST to merchant URL; in this project the request is received by api_gateway and **proxied** to billing_service (see api_gateway webhooks). Billing route: POST /webhooks/yookassa (no X-Service-Key required; ServiceAuthMiddleware skips /webhooks).
- **Handler:** `YooKassaService.verify_notification(body, ip)` then `BillingService.process_payment_notification(notification)`.
- **Request:** Raw body (JSON); IP used for allowlist check (YooKassa trusted IPs only). If IP not trusted, raises `ValidationError`.
- **Notification shape:** Caller uses `notification.get("object", notification)` and then:
  - `object.id` (payment id)
  - `object.status` ("succeeded", "canceled", etc.)
- **Response:** 200 with `{"status": "ok"}` after processing.
- **Idempotency:** process_payment_notification checks order status; if already PAID, returns without changing state.

---

## Main response statuses (outgoing)

- **200:** Payment created; response has id and confirmation.confirmation_url.
- **4xx/5xx:** raise_for_status() in code; billing will get exception (e.g. validation error from YooKassa).

---

## Main errors (caller side)

- **Outgoing:** Any httpx HTTP error propagates; billing create_order will fail and not persist payment_url if YooKassa fails.
- **Incoming (webhook):** ValidationError if IP not in trusted list. Other errors handled inside process_payment_notification (missing id, unknown order, already paid — no exception to client).

---

## Idempotency

- **Outgoing:** Each create_payment uses a new UUID as Idempotence-Key; so each call is a new payment. Billing creates one order per call, so one payment per order. Retrying create_order would create a new order and new payment (not idempotent at billing level).
- **Incoming:** Processing is idempotent: if order already PAID, handler returns without update.

---

## Happy path example

User starts payment:

1. Billing creates Order in DB, then calls `yookassa.create_payment(order_id, amount, currency, description)`.
2. YooKassa returns 200 with payment id and confirmation_url.
3. Billing saves payment_url and external_payment_id on order, commits, returns OrderRead to gateway/bot.
4. User is redirected to confirmation_url to pay.
5. Later YooKassa POSTs webhook to api_gateway → proxied to billing; billing verifies IP, parses notification, updates order status, creates subscription, calls vpn provision.

---

## Error path example

YooKassa returns 402 or 400 (e.g. invalid amount):

1. create_payment raises httpx.HTTPStatusError.
2. Billing create_order fails before commit (or on commit path); order may be created but without payment_url — depends on exact flow (in code, order is created first, then YooKassa, then flush/refresh/commit; so on YooKassa failure, exception propagates and commit is not reached for that request).

---

## Notes

- No shared Pydantic for YooKassa request/response; all dict-based. Stable for current use; if YooKassa API changes, only yookassa.py needs updating.
- **needs harmonization (minor):** For stub/mock in tests, a small interface (e.g. create_payment + verify_notification) would allow swapping real vs stub without touching BillingService logic.
