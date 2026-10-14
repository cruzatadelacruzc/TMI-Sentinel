from collections.abc import AsyncIterator

from fastapi import HTTPException
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import Settings


class Database:
    def __init__(self) -> None:
        self.engine = None
        self.session_factory: async_sessionmaker[AsyncSession] | None = None

    def initialize(self, settings: Settings) -> None:
        if not settings.database_url:
            return
        url = settings.database_url
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        parsed_url = make_url(url)
        connect_args = {}
        if parsed_url.port == 6543:
            connect_args["statement_cache_size"] = 0
        if parsed_url.query.get("ssl") == "require":
            connect_args["ssl"] = "require"
        self.engine = create_async_engine(
            parsed_url, pool_pre_ping=True, connect_args=connect_args
        )
        self.session_factory = async_sessionmaker(
            self.engine, expire_on_commit=False
        )

    async def close(self) -> None:
        if self.engine is not None:
            await self.engine.dispose()
            self.engine = None
            self.session_factory = None

    async def get_session(self) -> AsyncIterator[AsyncSession]:
        if self.session_factory is None:
            raise HTTPException(
                status_code=503,
                detail="DATABASE_URL is not configured",
            )
        async with self.session_factory() as session:
            yield session


database = Database()