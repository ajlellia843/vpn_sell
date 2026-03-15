from fastapi import APIRouter

from shared.database import DatabaseManager


def create_health_router(service_name: str, version: str, db: DatabaseManager) -> APIRouter:
    router = APIRouter(tags=["health"])

    @router.get("/health")
    async def health():
        db_ok = await db.check_connection()
        status = "ok" if db_ok else "degraded"
        return {
            "status": status,
            "service": service_name,
            "version": version,
            "checks": {"database": "ok" if db_ok else "unavailable"},
        }

    return router


def create_health_router_no_db(service_name: str, version: str) -> APIRouter:
    router = APIRouter(tags=["health"])

    @router.get("/health")
    async def health():
        return {"status": "ok", "service": service_name, "version": version}

    return router
