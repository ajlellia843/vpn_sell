# Contract: api_gateway → vpn_service

## Caller / Callee

- **Caller:** api_gateway (via `VPNServiceClient` from shared, used in `services/api_gateway/app/routes/bot.py` only in get_subscription)
- **Callee:** vpn_service (routes in `services/vpn_service/app/routes/vpn.py`, router prefix **/vpn**)
- **Transport:** HTTP, header `X-Service-Key: <service_api_key>`, shared `BaseHTTPClient`

---

## Endpoint used by api_gateway

### GET /access/{subscription_id}

- **Gateway usage:** `_vpn_client(request).get_access(subscription["id"])` when subscription exists; on NotFoundError gateway sets vpn_access to None
- **Client implementation:** `GET /access/{subscription_id}` (no /vpn prefix in client)
- **Request:** path `subscription_id` (UUID)
- **Actual vpn_service route:** `GET /vpn/access/{subscription_id}` (router has prefix `/vpn`)

**needs harmonization:** Shared `VPNServiceClient` uses path `/access/{subscription_id}`. vpn_service mounts routes with prefix `/vpn`, so the real path is `/vpn/access/{subscription_id}`. If gateway (and billing) use base_url without `/vpn` suffix, requests will 404. Either base_url must end with `/vpn`, or client paths must be prefixed with `/vpn`.

- **Response:** 200, `VPNAccessRead`: id, subscription_id, xui_client_id, inbound_id, connection_uri, provision_status, created_at, updated_at
- **provision_status:** enum "pending" | "provisioned" | "failed" | "disabled"
- **Errors:** 404 if access/binding not found; gateway catches NotFoundError and returns `vpn_access: null`

---

## Endpoints not used by api_gateway (used by billing_service)

For completeness; see [billing_to_vpn_service.md](billing_to_vpn_service.md):

- POST /provision → actually POST /vpn/provision
- POST /extend → POST /vpn/extend
- POST /disable → POST /vpn/disable
- POST /enable → POST /vpn/enable

Same path prefix issue applies.

---

## Main response statuses

- **200:** Success; VPNAccessRead JSON.
- **204:** Used by disable/enable (no body).
- **404:** Binding not found; shared NotFoundError.
- **4xx/5xx:** ServiceError.

---

## Main errors (caller side)

- `NotFoundError`: 404 (gateway catches and returns null vpn_access).
- `ServiceError`: other errors (would propagate to gateway).

---

## Idempotency

- GET /access/{id}: Idempotent.

---

## Happy path example

Gateway has subscription, fetches VPN link for user:

1. Call `vpn_client.get_access(subscription["id"])` (with base_url including /vpn or paths fixed).
2. vpn_service returns 200 with VPNAccessRead (connection_uri for client link).
3. Gateway returns `{"subscription": {...}, "vpn_access": {...}}` to bot.

---

## Error path example

No VPN binding yet (e.g. provision pending):

1. GET /vpn/access/{id} → 404.
2. Client raises NotFoundError.
3. Gateway catches, sets vpn_access to None, returns subscription with vpn_access: null.

---

## Notes

- **needs harmonization:** Path prefix mismatch between VPNServiceClient paths and vpn_service route prefix `/vpn`. Document in contract_gaps and fix either client paths or base_url in config.
