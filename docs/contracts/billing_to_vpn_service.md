# Contract: billing_service → vpn_service

## Caller / Callee

- **Caller:** billing_service (via `VPNServiceClient` from shared; used inside `BillingService` in `services/billing_service/app/services/billing.py`, injected from `request.app.state.vpn_client` in routes)
- **Callee:** vpn_service (routes in `services/vpn_service/app/routes/vpn.py`, router prefix **/vpn**)
- **Transport:** HTTP, header `X-Service-Key: <service_api_key>`, shared `BaseHTTPClient`

---

## Path prefix (needs harmonization)

vpn_service exposes routes under prefix **/vpn** (e.g. POST /vpn/provision, GET /vpn/access/{id}). Shared `VPNServiceClient` uses paths **without** `/vpn`: `/provision`, `/extend`, `/disable`, `/enable`, `/access/{id}`. So either:

- `vpn_service_url` in billing config must end with `/vpn`, or  
- VPNServiceClient must use paths prefixed with `/vpn`.

Below, "Effective path" assumes base_url includes /vpn or client is fixed to use /vpn.

---

## Endpoints

### POST /provision (effective: POST /vpn/provision)

- **Caller usage:** `BillingService.process_payment_notification` after creating subscription; calls `_vpn.provision(subscription_id, user_id, plan_duration_days, traffic_limit_gb, device_limit)`
- **Request:** JSON — `ProvisionRequest`: subscription_id (UUID), user_id (UUID), plan_duration_days (int), traffic_limit_gb (int | null), device_limit (int, default 1)
- **Response:** 200, `ProvisionResponse`: subscription_id, provision_status ("pending" | "provisioned" | "failed" | "disabled"), connection_uri (str | null)
- **Required response fields:** subscription_id, provision_status
- **Note:** Billing does not use response in a structured way; on exception it logs and leaves auto_provisioned False.

---

### POST /extend (effective: POST /vpn/extend)

- **Caller usage:** `BillingService.extend_subscription` after extending subscription in DB; calls `_vpn.extend(subscription_id, days)`
- **Request:** JSON — subscription_id (UUID), days (int)
- **Response:** 200, ProvisionResponse (subscription_id, provision_status, connection_uri)
- **Errors:** 404 if subscription/binding not found; billing catches exception, logs, continues (DB already updated).

---

### POST /disable (effective: POST /vpn/disable)

- **Caller usage:** `BillingService.revoke_subscription`; calls `_vpn.disable(subscription_id)`
- **Request:** JSON — subscription_id (UUID)
- **Response:** 204 No Content
- **Errors:** 404 if not found; billing catches, logs, continues.

---

### POST /enable (effective: POST /vpn/enable)

- **Caller usage:** Not used by billing in current code (revoke only uses disable).
- **Request:** JSON — subscription_id (UUID)
- **Response:** 204 No Content

---

## Main response statuses

- **200:** provision, extend — JSON body.
- **204:** disable, enable — no body.
- **404:** Subscription/binding not found; NotFoundError from BaseHTTPClient.
- **4xx/5xx:** ServiceError.

---

## Main errors (caller side)

- `NotFoundError`, `ServiceError` from BaseHTTPClient. Billing catches exceptions in process_payment_notification, extend_subscription, revoke_subscription and logs; does not fail the main flow (order/subscription state already updated in DB where applicable).

---

## Idempotency

- provision: Not idempotent; creates or updates VPN binding. Multiple calls for same subscription_id may be safe depending on vpn_service implementation (create or update).
- extend: Not idempotent; adds days.
- disable / enable: Idempotent in effect (setting state to disabled/enabled).

---

## Happy path example

Payment succeeded, billing creates subscription then provisions VPN:

1. billing creates Subscription in DB.
2. Call `vpn_client.provision(str(sub.id), str(order.user_id), plan.duration_days, plan.traffic_limit_gb, plan.device_limit)`.
3. vpn_service returns 200 with provision_status "provisioned" (or "pending"); billing sets sub.auto_provisioned = True and commits.

---

## Error path example

vpn_service unavailable or 404:

1. vpn_client.provision(...) raises ServiceError or NotFoundError.
2. Billing catches, logs exception, does not set auto_provisioned; commits order and subscription.
3. User has paid but VPN not provisioned; can be retried or handled by support.

---

## Notes

- **needs harmonization:** Same path prefix issue as api_gateway → vpn_service. Fix once in shared VPNServiceClient or in config (base_url with /vpn).
