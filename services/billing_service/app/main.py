from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI

from shared.clients.vpn import VPNServiceClient
from shared.database import DatabaseManager
from shared.exceptions import register_exception_handlers
from shared.health import create_health_router
from shared.logging import setup_logging
from shared.metrics import setup_metrics
from shared.service_auth import ServiceAuthMiddleware

from app.config import BillingServiceSettings
from app.routes import order, plan, subscription, webhook
from app.services.yookassa import YooKassaService

settings = BillingServiceSettings()

setup_logging(settings.service_name, settings.log_level)

db = DatabaseManager(
    db_url=settings.db_url,
    schema="billing",
    echo=settings.db_echo,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    await db.create_schema()

    _app.state.db = db
    _app.state.vpn_client = VPNServiceClient(
        base_url=settings.vpn_service_url,
        service_api_key=settings.service_api_key,
    )
    _app.state.yookassa = YooKassaService(
        shop_id=settings.yookassa_shop_id,
        secret_key=settings.yookassa_secret_key,
        return_url=settings.yookassa_return_url,
        webhook_secret=settings.yookassa_webhook_secret,
    )

    yield

    await _app.state.vpn_client.close()
    await db.close()


app = FastAPI(
    title="Billing Service",
    version=settings.service_version,
    lifespan=lifespan,
)

register_exception_handlers(app)
app.add_middleware(ServiceAuthMiddleware, expected_key=settings.service_api_key)
setup_metrics(app, settings.service_name)

app.include_router(create_health_router(settings.service_name, settings.service_version, db))
app.include_router(plan.router)
app.include_router(order.router)
app.include_router(subscription.router)
app.include_router(webhook.router)
