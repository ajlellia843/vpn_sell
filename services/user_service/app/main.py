from contextlib import asynccontextmanager

from fastapi import FastAPI

from shared.database import DatabaseManager
from shared.exceptions import register_exception_handlers
from shared.health import create_health_router
from shared.logging import get_logger, setup_logging
from shared.metrics import setup_metrics
from shared.service_auth import ServiceAuthMiddleware

from app.config import UserServiceSettings
from app.routes.user import router as user_router

settings = UserServiceSettings()

setup_logging(settings.service_name, settings.log_level, json_output=not settings.debug)
logger = get_logger(__name__)

db = DatabaseManager(
    settings.db_url,
    schema=settings.DB_SCHEMA,
    echo=settings.db_echo,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    await db.create_schema()
    logger.info("service started", service=settings.service_name)
    yield
    await db.close()
    logger.info("service stopped", service=settings.service_name)


app = FastAPI(
    title=settings.service_name,
    version=settings.service_version,
    lifespan=lifespan,
)

register_exception_handlers(app)
app.add_middleware(ServiceAuthMiddleware, expected_key=settings.service_api_key)
setup_metrics(app, settings.service_name)

app.include_router(
    create_health_router(settings.service_name, settings.service_version, db),
)
app.include_router(user_router)
