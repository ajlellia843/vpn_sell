from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from shared.database import Base, DatabaseManager
from shared.exceptions import register_exception_handlers
from shared.health import create_health_router
from shared.logging import setup_logging
from shared.metrics import setup_metrics

from app.auth import _LoginRedirectException, login_redirect_handler
from app.config import AdminServiceSettings
from app.models.audit_log import AuditLog  # noqa: F401 — register model with Base
from app.providers import provide_billing_client, provide_user_client, provide_vpn_client

APP_DIR = Path(__file__).resolve().parent

settings = AdminServiceSettings()

setup_logging(settings.service_name, settings.log_level, json_output=not settings.debug)

db = DatabaseManager(
    db_url=settings.db_url,
    schema="admin",
    echo=settings.db_echo,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    await db.create_schema()
    async with db.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    _app.state.user_client = provide_user_client(settings)
    _app.state.billing_client = provide_billing_client(settings)
    _app.state.vpn_client = provide_vpn_client(settings)

    yield

    await _app.state.user_client.close()
    await _app.state.billing_client.close()
    await _app.state.vpn_client.close()
    await db.close()


app = FastAPI(
    title="VPN Admin Service",
    version=settings.service_version,
    lifespan=lifespan,
)

app.state.settings = settings
app.state.db = db
app.state.templates = Jinja2Templates(directory=str(APP_DIR / "templates"))

app.mount("/static", StaticFiles(directory=str(APP_DIR / "static")), name="static")

register_exception_handlers(app)
app.add_exception_handler(_LoginRedirectException, login_redirect_handler)
setup_metrics(app, settings.service_name)

app.include_router(create_health_router(settings.service_name, settings.service_version, db))

from app.routes.dashboard import router as dashboard_router
from app.routes.orders import router as orders_router
from app.routes.plans import router as plans_router
from app.routes.subscriptions import router as subscriptions_router
from app.routes.users import router as users_router

app.include_router(dashboard_router)
app.include_router(users_router)
app.include_router(plans_router)
app.include_router(orders_router)
app.include_router(subscriptions_router)
