from datetime import datetime

from app.core.exceptions import MissingRateHistory
from app.core.rate_provider import RateProvider
from app.modules.analytics.buffer import calculate_buffer
from app.modules.analytics.schemas import VolatilityResponse
from app.modules.analytics.volatility import (
    calculate_daily_volatility,
    daily_observations,
)


class AnalyticsEngine:
    def __init__(self, provider: RateProvider) -> None:
        self.provider = provider

    async def volatility(
        self,
        currency: str,
        start: datetime | None = None,
        end: datetime | None = None,
        variant: str | None = None,
        source: str | None = None,
    ) -> VolatilityResponse:
        points = await self.provider.get_history(
            currency, start, end, variant=variant, source=source
        )
        observations = daily_observations(points)
        if len(observations) < 3:
            raise MissingRateHistory("At least three distinct days of rates are required")
        latest = observations[-1]
        return VolatilityResponse(
            currency=latest.currency,
            variant=latest.variant,
            source=latest.source,
            daily_volatility_pct=calculate_daily_volatility(observations),
            observations=len(observations),
            start=observations[0].observed_at,
            end=latest.observed_at,
        )

    async def buffer(
        self,
        currency: str,
        horizon_days: int = 7,
        confidence: float = 0.95,
        start: datetime | None = None,
        end: datetime | None = None,
        variant: str | None = None,
        source: str | None = None,
    ):
        points = await self.provider.get_history(
            currency, start, end, variant=variant, source=source
        )
        return calculate_buffer(points, horizon_days, confidence)