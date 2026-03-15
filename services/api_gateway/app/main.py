from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from shared.clients.billing import BillingServiceClient
from shared.clients.user import UserServiceClient
from shared.clients.vpn import VPNServiceClient
from shared.exceptions import register_exception_handlers
from shared.health import create_health_router_no_db
from shared.logging import setup_logging
from shared.metrics import setup_metrics

from app.config import GatewaySettings
from app.middleware.correlation import CorrelationIdMiddleware
from app.routes.bot import router as bot_router
from app.routes.webhooks import router as webhooks_router

settings = GatewaySettings()


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncIterator[None]:
    application.state.user_client = UserServiceClient(
        base_url=settings.user_service_url,
        service_api_key=settings.service_api_key,
    )
    application.state.billing_client = BillingServiceClient(
        base_url=settings.billing_service_url,
        service_api_key=settings.service_api_key,
    )
    application.state.vpn_client = VPNServiceClient(
        base_url=settings.vpn_service_url,
        service_api_key=settings.service_api_key,
    )
    application.state.billing_service_url = settings.billing_service_url

    yield

    await application.state.user_client.close()
    await application.state.billing_client.close()
    await application.state.vpn_client.close()


setup_logging(settings.service_name, settings.log_level)

app = FastAPI(
    title=settings.service_name,
    version=settings.service_version,
    debug=settings.debug,
    lifespan=lifespan,
)

register_exception_handlers(app)
app.add_middleware(CorrelationIdMiddleware)
setup_metrics(app, settings.service_name)

app.include_router(create_health_router_no_db(settings.service_name, settings.service_version))
app.include_router(bot_router)
app.include_router(webhooks_router)
