# VPN Subscription Platform

Production-ready MVP microservices platform for selling VPN subscriptions through a Telegram bot.

## Architecture

```
Telegram User ──► bot-service (aiogram 3) ──► api-gateway (BFF) ──┬── user-service
                                                                   ├── billing-service ──► YooKassa API
                                                                   └── vpn-service ──────► 3x-ui Panel
Admin Browser ──► admin-service (Jinja2 + HTMX)
```

### Services

| Service | Port | Description |
|---------|------|-------------|
| **api-gateway** | 8000 | BFF layer, aggregates calls for the bot |
| **user-service** | internal | User registration and management |
| **billing-service** | internal | Plans, orders, subscriptions, YooKassa payments |
| **vpn-service** | internal | VPN provisioning via 3x-ui adapter |
| **admin-service** | 8001 | Server-side admin panel |
| **bot-service** | - | Telegram bot (polling/webhook) |

### Tech Stack

- Python 3.12+, FastAPI, aiogram 3.x
- PostgreSQL 16 (schema-per-service)
- SQLAlchemy 2.x + Alembic
- httpx, Pydantic v2, structlog
- Docker Compose
- Prometheus + Grafana

## Quick Start

### 1. Clone and configure

```bash
git clone <repository-url>
cd vpn_sell
cp .env.example .env
```

Edit `.env` with your actual values:
- `BOT_TOKEN` - Telegram bot token from @BotFather
- `YOOKASSA_SHOP_ID` / `YOOKASSA_SECRET_KEY` - YooKassa credentials
- `XUI_BASE_URL` / `XUI_USERNAME` / `XUI_PASSWORD` - 3x-ui panel access
- `SERVICE_API_KEY` - random secret for inter-service auth
- `ADMIN_JWT_SECRET` - random secret for admin JWT tokens

### 2. Start the platform

```bash
docker compose up --build -d
```

### 3. Run database migrations

```bash
docker compose exec user-service alembic upgrade head
docker compose exec billing-service alembic upgrade head
docker compose exec vpn-service alembic upgrade head
```

The admin-service auto-creates its schema on startup.

### 4. Access services

- **Telegram Bot**: find your bot by the handle you configured with @BotFather
- **Admin Panel**: http://localhost:8001
- **API Gateway**: http://localhost:8000
- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090

## Environment Variables

### Core

| Variable | Description | Default |
|----------|-------------|---------|
| `POSTGRES_USER` | PostgreSQL user | `vpn` |
| `POSTGRES_PASSWORD` | PostgreSQL password | - |
| `POSTGRES_DB` | Database name | `vpn_platform` |
| `DATABASE_URL` | Full async connection string | - |
| `SERVICE_API_KEY` | Shared key for service-to-service auth | - |
| `LOG_LEVEL` | Logging level | `INFO` |

### Telegram Bot

| Variable | Description | Default |
|----------|-------------|---------|
| `BOT_TOKEN` | Telegram bot token | - |
| `BOT_MODE` | `polling` or `webhook` | `polling` |
| `WEBHOOK_URL` | Public webhook URL (webhook mode only) | - |

### YooKassa

| Variable | Description |
|----------|-------------|
| `YOOKASSA_SHOP_ID` | Shop ID |
| `YOOKASSA_SECRET_KEY` | API secret key |
| `YOOKASSA_RETURN_URL` | Redirect URL after payment |
| `YOOKASSA_WEBHOOK_SECRET` | Webhook signature secret |

### 3x-ui Panel

| Variable | Description | Default |
|----------|-------------|---------|
| `XUI_BASE_URL` | Panel URL | - |
| `XUI_USERNAME` | Panel login | `admin` |
| `XUI_PASSWORD` | Panel password | - |
| `XUI_INBOUND_ID` | Default inbound ID | `1` |

### Admin Panel

| Variable | Description |
|----------|-------------|
| `ADMIN_USERNAME` | Admin login |
| `ADMIN_PASSWORD_HASH` | bcrypt hash of admin password |
| `ADMIN_JWT_SECRET` | JWT signing secret |

## Project Structure

```
shared/                     Shared library (installed into each service image)
  shared/
    config.py               Base Pydantic settings
    database.py             Async SQLAlchemy engine/session
    logging.py              structlog JSON setup
    metrics.py              Prometheus middleware
    exceptions.py           Unified error responses
    health.py               Health check router factory
    repository.py           Generic async CRUD repository
    service_auth.py         X-Service-Key middleware
    schemas/                Pydantic API contracts
    clients/                Inter-service HTTP clients

services/
  api_gateway/              BFF gateway for bot-friendly API
  user_service/             User registration and management
  billing_service/          Plans, orders, subscriptions, payments
  vpn_service/              VPN provisioning + 3x-ui adapter
  admin_service/            Server-side admin panel (Jinja2 + HTMX)
  bot_service/              Telegram bot (aiogram 3.x)

infra/
  prometheus/               Prometheus config
  grafana/                  Grafana provisioning + dashboards
```

## Bot-Friendly API (Gateway)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/bot/me` | Register or get user + active subscription |
| GET | `/bot/me?telegram_id=N` | Get user + subscription |
| GET | `/bot/plans` | List active plans |
| POST | `/bot/orders` | Create order + payment |
| GET | `/bot/orders/{id}` | Check order status |
| GET | `/bot/subscription?telegram_id=N` | Active subscription + VPN access |
| POST | `/bot/subscription/extend` | Extend subscription |
| POST | `/webhooks/yookassa` | YooKassa payment webhook |

## Database Design

Each service owns its PostgreSQL schema:

- `users` schema: `users` table
- `billing` schema: `plans`, `orders`, `subscriptions` tables
- `vpn` schema: `vpn_access_bindings` table
- `admin` schema: `audit_logs` table

No cross-schema foreign keys. References between services use UUIDs resolved via HTTP APIs.

## Development

### Adding a new migration

```bash
cd services/user_service
alembic revision --autogenerate -m "description"
```

### Generate admin password hash

```python
import bcrypt
print(bcrypt.hashpw(b"your-password", bcrypt.gensalt()).decode())
```

### Logs

All services output structured JSON logs to stdout. Use `docker compose logs -f <service>` to follow.

## Monitoring

Prometheus scrapes `/metrics` from every service. Grafana auto-provisions with:

- Request rate per service
- Error rate per service
- Latency percentiles (p50/p95/p99)
- Active subscriptions gauge
- Payment success/failure rate
- VPN provision attempts and latency
- Telegram bot update rate

## Roadmap

1. Redis for FSM storage + response caching
2. Event-driven architecture (Redis Streams / Kafka)
3. Webhook mode for Telegram bot
4. Multi-admin RBAC
5. Payment retry and reconciliation cron
6. Subscription expiry cron job
7. Distributed rate limiting via Redis
8. CI/CD pipeline
9. Kubernetes manifests
10. PostgreSQL backup strategy
