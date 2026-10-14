from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import create_provider
from app.database import database
from app.modules.analytics.engine import AnalyticsEngine
from app.modules.analytics.schemas import (
    BufferRequest,
    BufferResponse,
    VolatilityResponse,
)

router = APIRouter()


@router.get("/volatility", response_model=VolatilityResponse)
async def get_volatility(
    request: Request,
    currency: str = Query(min_length=3, max_length=12),
    source: str = "eltoque",
    variant: str | None = None,
    start: datetime | None = None,
    end: datetime | None = None,
    session: AsyncSession = Depends(database.get_session),
) -> VolatilityResponse:
    if source in {"bcc", "bcc_fallback"} and variant is None:
        raise HTTPException(
            status_code=422,
            detail="variant is required for BCC sources",
        )
    provider = create_provider(source, session, request)
    return await AnalyticsEngine(provider).volatility(
        currency.upper(), start, end, variant=variant, source=source
    )


@router.post("/buffer", response_model=BufferResponse)
async def calculate_exchange_buffer(
    body: BufferRequest,
    request: Request,
    start: datetime | None = None,
    end: datetime | None = None,
    session: AsyncSession = Depends(database.get_session),
) -> BufferResponse:
    if body.source in {"bcc", "bcc_fallback"} and body.variant is None:
        raise HTTPException(
            status_code=422,
            detail="variant is required for BCC sources",
        )
    provider = create_provider(body.source, session, request)
    return await AnalyticsEngine(provider).buffer(
        body.currency.upper(),
        body.horizon_days,
        body.confidence,
        start,
        end,
        variant=body.variant,
        source=body.source,
    )