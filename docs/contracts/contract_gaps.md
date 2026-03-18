# Contract Gaps and Harmonization

Summary of DTO/response mismatches, unclear shapes, stub-client implications, and stability of current contracts.

---

## 1. DTO / response shape mismatches between services

### 1.1 billing_service list endpoints vs admin_service expectation

- **billing_service** `GET /orders/` and `GET /subscriptions/` return a **JSON array** (FastAPI `response_model=list[OrderRead]` / `list[SubscriptionRead]`).
- **admin_service** uses `resp.get("items", [])` and `resp.get("total", 0)`. A list has no `.get()`, so this causes **AttributeError** at runtime when admin loads orders or subscriptions (or dashboard counts).
- **Gap:** Paginated contract (items + total) is expected by admin but not provided by billing. Either:
  - billing_service should return `{"items": [...], "total": N}` and add total count (e.g. from repo), or
  - admin_service should treat response as a plain list and compute total from length (losing real total count for pagination).
- **Recommendation:** Define a single paginated response shape in shared (e.g. `ItemsResponse[T]`) and use it in billing for list_orders and list_subscriptions; keep admin’s expectation.

### 1.2 user_service list vs admin

- **user_service** `GET /users/` returns `{"items": [...], "total": total}`. Admin uses `resp.get("items", [])` and `resp.get("total", 0)`. **No mismatch.**

### 1.3 bot ↔ api_gateway: no shared DTOs

- api_gateway defines its own request bodies (RegisterBody, CreateOrderBody, ExtendSubscriptionBody) and returns plain `dict[str, Any]` (or list of dicts for plans).
- bot_service uses dict access; no Pydantic models for gateway responses. Types (user, subscription, order, plan) are not validated on the bot side.
- **Gap:** No shared response DTOs on this boundary; unclear shape for new consumers or stubs. Prefer introducing shared (or gateway-specific) response models and optionally using them in the bot for validation.

---

## 2. Unclear or implicit response shapes

### 2.1 get_active_subscription return type

- **BillingServiceClient.get_active_subscription** catches all exceptions and returns **None**. So the response is either a SubscriptionRead object or None; no distinction between 404 and 5xx. Caller (api_gateway) treats both as “no subscription”. Shape is clear; behavior is intentional but could be documented (e.g. “returns None on any error”).

### 2.2 YooKassa create_payment return

- **YooKassaService.create_payment** returns `{"payment_id": str, "confirmation_url": str}`. Not a Pydantic model; stable but undocumented in types. Fine for current use; for stubs, a small typed dataclass or Pydantic model would help.

### 2.3 3x-ui panel responses

- XUIAdapter uses panel JSON as dicts; no formal schema. Stable for current panel version; changes in 3x-ui API require adapter-only changes.

---

## 3. Future problems for stub / real abstraction

### 3.1 Bot → api_gateway

- **APIClient** is concrete; no interface. To introduce a stub (e.g. for tests or offline bot), one would either subclass/mock APIClient or define an abstract interface (protocol) and have APIClient implement it. Response types are dicts, so stub can return dicts without shared models.
- **Recommendation:** Introduce a small protocol (e.g. `BotGatewayClient`) with the current methods and use it in handlers; then real and stub implementations become swappable.

### 3.2 api_gateway / billing / admin → internal services

- Shared clients (UserServiceClient, BillingServiceClient, VPNServiceClient) are concrete. They already use a common base (BaseHTTPClient). For stubs, one could:
  - Subclass and override methods, or
  - Introduce interfaces (protocols) and register real vs stub in app state. No interface exists today; adding one would make stub injection straightforward.

### 3.3 BillingService → YooKassa and VPN

- **BillingService** depends on concrete `YooKassaService` and `VPNServiceClient`. No interface. To stub payments or VPN in tests, one must replace these in the BillingService constructor (or via app state). Introducing small interfaces (e.g. PaymentProvider, VPNProvisioner) would allow stub/real swap without changing BillingService method signatures.

### 3.4 vpn_service → 3x-ui

- **AbstractVPNPanelAdapter** already exists; XUIAdapter is one implementation. Stub or another panel = another implementation. **Already suitable** for abstraction.

---

## 4. Contract stability summary

| Contract | Stable? | Notes |
|---------|--------|--------|
| api_gateway → user_service | Yes | Shared UserCreate/UserRead; response shape clear. |
| api_gateway → billing_service | Yes | Shared PlanRead, OrderRead, SubscriptionRead; get_active_subscription returns None on error by design. |
| api_gateway → vpn_service | **No** | Path prefix mismatch: client uses /provision, /access/…; service uses /vpn/provision, /vpn/access/…. Fix client or base_url. |
| billing_service → vpn_service | **No** | Same path prefix issue as above. |
| billing_service → YooKassa | Yes | Dict-based; stable for current usage. Optional: add small DTO for create_payment return. |
| vpn_service → 3x-ui | Yes | Adapter encapsulates panel; AbstractVPNPanelAdapter allows swapping. |
| bot → api_gateway | Partial | Works; no shared response DTOs, no interface for stubs. |
| admin → user_service | Yes | user_service returns {items, total}; admin expects that. |
| admin → billing_service | **No** | list_orders and list_subscriptions return array; admin expects {items, total}. Causes runtime error. |

---

## 5. Prioritized harmonization and abstraction

1. **Critical (runtime bug):** Align billing list_orders and list_subscriptions with admin expectation: either return `{items, total}` from billing or change admin to use plain list and accept no total (prefer adding total in billing).
2. **Critical (integration bug):** Fix VPN path prefix: either set vpn_service base_url to include `/vpn` for all callers (api_gateway, billing, admin) or change shared VPNServiceClient to use paths prefixed with `/vpn`.
3. **Stub/abstraction (high value):** Define a small protocol for bot → api_gateway (e.g. get_me, get_plans, create_order, get_order, get_subscription, extend_subscription) so that stub and real APIClient can be swapped in tests or tooling.
4. **Stub/abstraction (medium):** Add interfaces for BillingService dependencies (payment provider, VPN client) to allow stubbing in tests without touching business logic.
5. **Optional:** Introduce shared or gateway response DTOs for bot ↔ api_gateway to make the contract explicit and easier to stub/maintain.
