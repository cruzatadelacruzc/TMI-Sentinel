from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.v1.router import router
from app.config import get_settings
from app.core.base_model import Base
from app.core.exceptions import CalculationError, ConfigurationError, DataSourceError
from app.core.logging import configure_logging
from app.database import database
from app.modules.bcc.models import BccRate
from app.modules.eltoque.models import ElToqueRate
from app.scheduler.manager import SchedulerManager
from app.scheduler.models import SchedulerSettings

_REGISTERED_MODELS = (BccRate, ElToqueRate, SchedulerSettings)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    configure_logging(settings.log_level)
    database.initialize(settings)
    app.state.settings = settings
    app.state.database = database
    app.state.scheduler_manager = None
    try:
        if database.engine is not None and database.session_factory is not None:
            async with database.engine.begin() as connection:
                await connection.run_sync(Base.metadata.create_all)
            manager = SchedulerManager(settings, database.session_factory)
            await manager.configure()
            app.state.scheduler_manager = manager
        yield
    finally:
        if app.state.scheduler_manager is not None:
            await app.state.scheduler_manager.shutdown()
        await database.close()


app = FastAPI(title="TMI Sentinel API", version="1.0.0", lifespan=lifespan)
app.include_router(router, prefix="/api/v1")


@app.exception_handler(DataSourceError)
async def handle_data_source_error(
    request: Request, exc: DataSourceError
) -> JSONResponse:
    return JSONResponse(status_code=502, content={"detail": str(exc)})


@app.exception_handler(CalculationError)
async def handle_calculation_error(
    request: Request, exc: CalculationError
) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": str(exc)})


@app.exception_handler(ConfigurationError)
async def handle_configuration_error(
    request: Request, exc: ConfigurationError
) -> JSONResponse:
    return JSONResponse(status_code=500, content={"detail": str(exc)})