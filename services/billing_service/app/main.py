from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI

from shared.database import DatabaseManager
from shared.exceptions import register_exception_handlers
from shared.health import create_health_router
from shared.logging import setup_logging
from shared.metrics import setup_metrics
from shared.service_auth import ServiceAuthMiddleware

from app.config import BillingServiceSettings
from app.providers import provide_payment_provider, provide_vpn_client
from app.routes import order, plan, subscription, webhook

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
    _app.state.vpn_client = provide_vpn_client(settings)
    _app.state.yookassa = provide_payment_provider(settings)

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
