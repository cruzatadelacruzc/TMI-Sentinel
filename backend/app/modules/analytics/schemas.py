from datetime import datetime

from pydantic import BaseModel, Field


class VolatilityResponse(BaseModel):
    currency: str
    variant: str
    source: str
    daily_volatility_pct: float
    observations: int
    start: datetime
    end: datetime


class BufferResponse(VolatilityResponse):
    latest_rate: float
    horizon_days: int
    confidence: float
    spread_pct: float
    buffer_pct: float
    buffered_rate: float


class BufferRequest(BaseModel):
    currency: str = Field(min_length=3, max_length=12)
    horizon_days: int = Field(default=7, ge=1, le=90)
    confidence: float = Field(default=0.95, gt=0.5, lt=1)
    variant: str | None = None
    source: str = "eltoque"