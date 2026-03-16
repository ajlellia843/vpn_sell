from collections.abc import AsyncGenerator

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession


async def get_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    # #region agent log
    import sqlalchemy; print(f"[DEBUG-68820d] H1: sqlalchemy.__version__={sqlalchemy.__version__}", flush=True)
    sf = request.app.state.db.session_factory
    print(f"[DEBUG-68820d] H1: session_factory.kw={sf.kw}", flush=True)
    # #endregion
    async with request.app.state.db.session_factory() as session:
        yield session
