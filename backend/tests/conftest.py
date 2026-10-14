import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.config import get_settings
from app.core.base_model import Base
from app.database import database
from app.modules.bcc import models as bcc_models
from app.modules.eltoque import models as eltoque_models
from app.scheduler import models as scheduler_models


@pytest.fixture
def test_database_url(monkeypatch, tmp_path):
    database_url = f"sqlite+aiosqlite:///{tmp_path / 'test.db'}"
    monkeypatch.setenv("DATABASE_URL", database_url)
    monkeypatch.setenv("EL_TOQUE_API_TOKEN", "test-token")
    monkeypatch.setenv("SCHEDULER_ENABLED", "false")
    monkeypatch.delenv("SCHEDULER_INTERVAL_MINUTES", raising=False)
    get_settings.cache_clear()
    yield database_url
    get_settings.cache_clear()


@pytest.fixture
def client(test_database_url):
    from app.main import app

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        if database.engine is not None:
            import asyncio

            asyncio.run(database.close())
        get_settings.cache_clear()


@pytest_asyncio.fixture
async def db_session(test_database_url):
    engine = create_async_engine(test_database_url)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        yield session
    await engine.dispose()