from contextlib import asynccontextmanager

from fastapi import FastAPI

from shared.database import DatabaseManager
from shared.exceptions import register_exception_handlers
from shared.health import create_health_router
from shared.logging import get_logger, setup_logging
from shared.metrics import setup_metrics
from shared.service_auth import ServiceAuthMiddleware

from app.adapters.xui import XUIAdapter
from app.config import VPNServiceSettings
from app.routes.vpn import router as vpn_router

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings: VPNServiceSettings = app.state.settings
    db: DatabaseManager = app.state.db

    await db.create_schema()

    adapter = XUIAdapter(
        base_url=settings.xui_base_url,
        username=settings.xui_username,
        password=settings.xui_password,
        inbound_id=settings.xui_inbound_id,
    )
    await adapter.authenticate()
    app.state.vpn_adapter = adapter

    logger.info("vpn_service_started", version=settings.service_version)
    yield

    await adapter.close()
    await db.close()


def create_app() -> FastAPI:
    settings = VPNServiceSettings()

    setup_logging(
        settings.service_name,
        settings.log_level,
        json_output=not settings.debug,
    )

    app = FastAPI(
        title=settings.service_name,
        version=settings.service_version,
        docs_url="/docs" if settings.debug else None,
        lifespan=lifespan,
    )

    db = DatabaseManager(
        db_url=settings.db_url,
        schema="vpn",
        echo=settings.db_echo,
        pool_size=settings.db_pool_size,
        max_overflow=settings.db_max_overflow,
    )

    app.state.settings = settings
    app.state.db = db

    register_exception_handlers(app)
    app.add_middleware(ServiceAuthMiddleware, expected_key=settings.service_api_key)
    setup_metrics(app, settings.service_name)

    app.include_router(
        create_health_router(settings.service_name, settings.service_version, db),
    )
    app.include_router(vpn_router)

    return app


app = create_app()
