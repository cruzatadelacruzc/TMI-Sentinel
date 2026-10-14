import math
from statistics import NormalDist

from app.core.exceptions import MissingRateHistory
from app.core.rate_provider import RatePoint
from app.modules.analytics.schemas import BufferResponse
from app.modules.analytics.volatility import calculate_daily_volatility, daily_observations


def calculate_buffer(
    points: list[RatePoint], horizon_days: int, confidence: float
) -> BufferResponse:
    observations = daily_observations(points)
    if len(observations) < 3:
        raise MissingRateHistory("At least three distinct days of rates are required")
    volatility = calculate_daily_volatility(observations)
    spreads = [
        (point.sell_rate - point.buy_rate)
        / ((point.sell_rate + point.buy_rate) / 2)
        * 100
        for point in observations
        if point.buy_rate is not None
        and point.sell_rate is not None
        and point.buy_rate > 0
        and point.sell_rate >= point.buy_rate
    ]
    spread_pct = sum(spreads) / len(spreads) if spreads else 0.0
    z_score = NormalDist().inv_cdf(confidence)
    buffer_pct = volatility * math.sqrt(horizon_days) * z_score + spread_pct / 2
    latest = observations[-1]
    return BufferResponse(
        currency=latest.currency,
        variant=latest.variant,
        source=latest.source,
        daily_volatility_pct=volatility,
        observations=len(observations),
        start=observations[0].observed_at,
        end=latest.observed_at,
        latest_rate=latest.rate,
        horizon_days=horizon_days,
        confidence=confidence,
        spread_pct=spread_pct,
        buffer_pct=buffer_pct,
        buffered_rate=latest.rate * (1 + buffer_pct / 100),
    )