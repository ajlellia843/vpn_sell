from collections.abc import AsyncGenerator
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


def build_engine(
    db_url: str,
    echo: bool = False,
    pool_size: int = 5,
    max_overflow: int = 10,
    execution_options: dict[str, Any] | None = None,
):
    kwargs: dict[str, Any] = {
        "echo": echo,
        "pool_size": pool_size,
        "max_overflow": max_overflow,
        "pool_pre_ping": True,
    }
    if execution_options:
        kwargs["execution_options"] = execution_options
    return create_async_engine(db_url, **kwargs)


def build_session_factory(engine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine, expire_on_commit=False)


class DatabaseManager:
    """Manages async engine + session factory for a service."""

    def __init__(
        self,
        db_url: str,
        schema: str | None = None,
        echo: bool = False,
        pool_size: int = 5,
        max_overflow: int = 10,
    ) -> None:
        exec_opts = None
        if schema:
            exec_opts = {"schema_translate_map": {None: schema}}

        # #region agent log
        import sqlalchemy; print(f"[DEBUG-68820d] H1-fix: sqlalchemy={sqlalchemy.__version__}, schema={schema}, exec_opts={exec_opts}", flush=True)
        # #endregion

        self.engine = build_engine(
            db_url, echo=echo, pool_size=pool_size,
            max_overflow=max_overflow, execution_options=exec_opts,
        )
        self._schema = schema
        self.session_factory = async_sessionmaker(self.engine, expire_on_commit=False)

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.session_factory() as session:
            yield session

    async def check_connection(self) -> bool:
        try:
            async with self.engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            return True
        except Exception:
            return False

    async def close(self) -> None:
        await self.engine.dispose()

    async def create_schema(self) -> None:
        if not self._schema:
            return
        async with self.engine.begin() as conn:
            await conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {self._schema}"))
