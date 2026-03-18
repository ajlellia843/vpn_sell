# Contract: vpn_service → 3x-ui Panel (X-UI)

## Caller / Callee

- **Caller:** vpn_service (`XUIAdapter` in `services/vpn_service/app/adapters/xui.py`); used by `ProvisioningService` in `services/vpn_service/app/services/provisioning.py`
- **Callee:** 3x-ui Panel API (external); base URL from config (xui_base_url)
- **Transport:** HTTP, session-based (login first; cookie/session); httpx.AsyncClient with retry (tenacity) on adapter methods

---

## Authentication

### POST /login

- **Caller usage:** `XUIAdapter.authenticate()` at startup (called from vpn_service lifespan).
- **Request:** form body `username`, `password` (from config).
- **Response:** success: 200, JSON with `success: true`; adapter sets _authenticated = True. On failure: body may have `success: false`, `msg`; adapter raises RuntimeError.
- **401:** Adapter retries once (clears _authenticated, re-authenticates, retries request).

---

## Client management

### POST /panel/api/inbounds/addClient

- **Caller usage:** `adapter.create_client(client_id, email, total_gb, expiry_days, device_limit)`
- **Request:** JSON — `id` (inbound_id), `settings` (JSON string): object with `clients`: [{ id, email, totalGB, expiryTime (ms), limitIp, enable: true }]
- **totalGB:** total_gb * 1024^3; expiryTime: Unix ms (now + expiry_days * 86400) * 1000
- **Response:** Panel-specific; adapter does not parse structured result beyond raise_for_status().
- **Idempotency:** Not guaranteed; same client_id might conflict or update depending on panel.

---

### GET /panel/api/inbounds/getClientTraffics/{client_id}

- **Caller usage:** `adapter.get_client(client_id)` — returns client object or None if 404 or success false.
- **Request:** path client_id.
- **Response:** 200 with success and obj; adapter returns obj or None. 404 → None.

---

### POST /panel/api/inbounds/updateClient/{client_id}

- **Caller usage:** `adapter.extend_client(client_id, days)`, `adapter.disable_client(client_id)`, `adapter.enable_client(client_id)`
- **Request:** JSON — `id` (inbound_id), `settings` (JSON string): for extend — clients with expiryTime; for disable/enable — clients with enable false/true.
- **Response:** Panel-specific; adapter uses raise_for_status().

---

### GET /panel/api/inbounds/get/{inbound_id}

- **Caller usage:** `adapter.get_client_link(client_id, inbound_id)` — fetches inbound config to build vless/vmess link.
- **Request:** path inbound_id.
- **Response:** success, obj (listen, port, protocol, streamSettings, remark, etc.); adapter builds connection URI string (vless://... or vmess://...).
- **Errors:** If not success, raises RuntimeError. Unsupported protocol raises RuntimeError.

---

## Main response statuses

- **200:** Success for login, addClient, updateClient, getClientTraffics, get.
- **401:** Login required or expired; adapter re-authenticates and retries once.
- **404:** get_client returns None.

---

## Main errors (caller side)

- **RuntimeError:** Login failed (success false), get_client_link failed (success false), unsupported protocol.
- **httpx.HTTPStatusError:** Other HTTP errors; propagate from adapter (with retry on 401 for _request).

---

## Idempotency

- extend_client: Reads current expiry then adds days; effectively additive, not idempotent for same request.
- disable_client / enable_client: Idempotent (set enable to false/true).
- create_client: Depends on panel; duplicate client_id may error or overwrite.

---

## Happy path example

Provision new subscription:

1. ProvisioningService creates/gets binding in DB, then calls `adapter.create_client(client_id, email, total_gb, expiry_days, device_limit)`.
2. XUIAdapter POSTs addClient; panel returns 200.
3. ProvisioningService calls `adapter.get_client_link(client_id, inbound_id)` to get vless/vmess link.
4. Returns ProvisionResponse with connection_uri to vpn_service route → client.

---

## Error path example

Panel returns 500 on addClient:

1. _request raises HTTPStatusError (after retries).
2. ProvisioningService propagates; vpn route returns 5xx; billing catches and logs (subscription already created, auto_provisioned stays False).

---

## Notes

- Contract is internal to vpn_service; only XUIAdapter talks to panel. AbstractVPNPanelAdapter allows swapping implementation (e.g. another panel). Response shapes from 3x-ui are not formally defined in code (dict-based). Stable for current X-UI version; panel API changes require adapter changes only.
