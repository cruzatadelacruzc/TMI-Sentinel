from datetime import datetime

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import database
from app.modules.eltoque.client import ElToqueClient
from app.modules.eltoque.repository import ElToqueRepository
from app.modules.eltoque.schemas import ElToqueRateResponse
from app.modules.eltoque.service import ElToqueService

router = APIRouter()


@router.post("/ingest")
async def ingest_eltoque(
    request: Request,
    session: AsyncSession = Depends(database.get_session),
) -> dict[str, int]:
    service = ElToqueService(session, ElToqueClient(request.app.state.settings))
    return {"saved": await service.ingest()}


@router.get("/rates", response_model=list[ElToqueRateResponse])
async def get_eltoque_rates(
    currency: str = Query(min_length=3, max_length=12),
    start: datetime | None = None,
    end: datetime | None = None,
    variant: str | None = None,
    session: AsyncSession = Depends(database.get_session),
) -> list[ElToqueRateResponse]:
    records = await ElToqueRepository(session).list_range(
        currency.upper(), start, end, variant=variant
    )
    return [ElToqueRateResponse.model_validate(record) for record in records]