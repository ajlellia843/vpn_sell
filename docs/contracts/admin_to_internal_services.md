# Contract: admin_service → user_service and billing_service

## Caller / Callee

- **Caller:** admin_service (Jinja2 + HTMX; routes in `services/admin_service/app/routes/` — users, plans, orders, subscriptions, dashboard)
- **Callees:** user_service (UserServiceClient), billing_service (BillingServiceClient). vpn_client is created in lifespan but **not used** by any admin route.
- **Transport:** HTTP, header `X-Service-Key: <service_api_key>`, shared clients from `request.app.state`

---

## admin_service → user_service

### GET /users/by-telegram/{telegram_id}

- **Admin usage:** When user searches by telegram_id (form field); `user_client.get_by_telegram_id(int(telegram_id))`
- **Request:** path telegram_id (int)
- **Response:** 200, UserRead (id, telegram_id, username, first_name, is_active, created_at, updated_at)
- **Errors:** 404; admin catches Exception and shows empty list.

---

### GET /users/

- **Admin usage:** `user_client.list_users(offset, limit)` — dashboard (count) and users list.
- **Request:** query offset (int), limit (int); client default limit 50.
- **Response:** 200, **shape:** `{"items": [UserRead, ...], "total": int}` (user_service returns this shape)
- **Required:** items (array), total (int). Admin uses `resp.get("items", [])`, `resp.get("total", 0)`.

---

## admin_service → billing_service

### GET /plans/

- **Admin usage:** `billing_client.list_plans()` — plans list page and new plan form context.
- **Request:** none
- **Response:** 200, **JSON array** of PlanRead (billing returns list directly, not {items, total}). Admin uses result as list: `plans = await billing_client.list_plans()` → plans is the array. **No mismatch.**

---

### POST /plans/

- **Admin usage:** create_plan; form data mapped to dict: name, duration_days, price (string), currency, description, traffic_limit_gb, device_limit, is_active.
- **Request:** JSON — PlanCreate-like (name, duration_days, price, currency, description, traffic_limit_gb, device_limit, is_active). Admin sends form and builds dict; price as string.
- **Response:** 201, PlanRead
- **Errors:** 4xx; admin does not parse error body, redirects on success.

---

### GET /plans/{plan_id}

- **Admin usage:** `billing_client.get_plan(plan_id)` for edit form.
- **Response:** 200, PlanRead
- **Errors:** 404

---

### PUT /plans/{plan_id}

- **Admin usage:** update_plan; form → dict (same shape as create).
- **Request:** JSON PlanUpdate-like
- **Response:** 200, PlanRead

---

### GET /orders/

- **Admin usage:** `billing_client.list_orders(offset, limit, status)` for orders list and dashboard.
- **Request:** query offset, limit, status (optional)
- **Response (billing_service actual):** 200, **JSON array** of OrderRead (route returns `list[OrderRead]`, i.e. array).
- **Admin expectation:** `resp.get("items", [])`, `resp.get("total", 0)` — i.e. admin expects **object with items and total**, but billing returns a **plain array**. So `resp` is a list; `resp.get("items", [])` would raise **AttributeError** (list has no .get). **needs harmonization.**

---

### GET /subscriptions/

- **Admin usage:** `billing_client.list_subscriptions(offset, limit, status)` for subscriptions list and dashboard.
- **Request:** query offset, limit, status (optional)
- **Response (billing_service actual):** 200, **JSON array** of SubscriptionRead (route returns list).
- **Admin expectation:** `resp.get("items", [])`, `resp.get("total", 0)` — same mismatch as orders. **needs harmonization.**

---

### POST /subscriptions/{sub_id}/extend

- **Admin usage:** `billing_client.extend_subscription(sub_id, days)`; form field "days".
- **Request:** path sub_id, JSON body `{"days": int}`
- **Response:** 200, SubscriptionRead
- **Errors:** 404; admin redirects on success.

---

### POST /subscriptions/{sub_id}/revoke

- **Admin usage:** `billing_client.revoke_subscription(sub_id)`
- **Request:** path sub_id, no body
- **Response:** 200, SubscriptionRead
- **Errors:** 404

---

## Dashboard

- **user_client.list_users(offset=0, limit=1)** → expects `total` for total_users count. user_service returns {items, total} — **OK**.
- **billing_client.list_subscriptions(offset=0, limit=1, status="active")** → expects `total`; billing returns array — **needs harmonization** (admin uses resp.get("total", 0); for list, this would be 0 and items would be resp.get("items", []) which for a list is AttributeError; so dashboard would crash when trying to get total from list).
- **billing_client.list_orders(offset=0, limit=10)** → same; admin expects items and total — **needs harmonization**.

---

## Main response statuses

- 200/201: Success.
- 404: NotFound; admin often catches generic Exception and shows empty or redirects.

---

## Main errors (caller side)

- Admin uses broad `try/except Exception`; does not distinguish error types. No shared error DTO parsing.

---

## Idempotency

- GETs: Idempotent. POST/PUT: create_plan, update_plan, extend_subscription, revoke_subscription — not idempotent (or revoke is idempotent in effect).

---

## Happy path example

Admin opens orders list:

1. Admin calls `billing_client.list_orders(offset, limit, status)`.
2. **If billing returned {items, total}:** admin would use items and total for table and pagination. **Current billing returns array:** admin code would crash on resp.get("items", []) unless fixed. See contract_gaps.

---

## Error path example

Billing unavailable:

1. Client raises ServiceError or connection error.
2. Admin catches Exception, passes empty list or zero counts to template.
3. Page renders with empty data.

---

## Notes

- **needs harmonization:** billing_service list_orders and list_subscriptions return a **list**, while admin (and common API style) expects **{ items: [], total: N }**. Either billing should return paginated shape with total, or admin should treat response as list and not use .get("items", "total"). Document in contract_gaps.
- **Unused dependency:** admin_service creates vpn_client in lifespan but no route uses it; can be removed from state or reserved for future use.
