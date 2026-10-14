from datetime import datetime

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import database
from app.modules.bcc.client import BccClient
from app.modules.bcc.fallback import BccFallbackClient
from app.modules.bcc.repository import BccRepository
from app.modules.bcc.schemas import BccRateResponse
from app.modules.bcc.service import BccService

router = APIRouter()


def _service(request: Request, session: AsyncSession) -> BccService:
    settings = request.app.state.settings
    return BccService(
        session,
        BccClient(settings),
        BccFallbackClient(settings) if settings.bcc_fallback_api_url else None,
    )


@router.post("/ingest")
async def ingest_bcc(
    request: Request,
    session: AsyncSession = Depends(database.get_session),
) -> dict[str, int]:
    return {"saved": await _service(request, session).ingest()}


@router.get("/rates", response_model=list[BccRateResponse])
async def get_bcc_rates(
    currency: str = Query(min_length=3, max_length=12),
    start: datetime | None = None,
    end: datetime | None = None,
    variant: str | None = None,
    source: str = "bcc",
    session: AsyncSession = Depends(database.get_session),
) -> list[BccRateResponse]:
    records = await BccRepository(session).list_range(
        currency.upper(), start, end, variant=variant, provider=source
    )
    return [BccRateResponse.model_validate(record) for record in records]