import asyncio
from datetime import UTC, datetime, timedelta

import pytest

from app.core.exceptions import MissingRateHistory
from app.core.rate_provider import RatePoint
from app.modules.analytics.engine import AnalyticsEngine


class InMemoryProvider:
    def __init__(self, points: list[RatePoint]) -> None:
        self.points = points

    async def get_history(self, currency, start=None, end=None, variant=None, source=None):
        assert currency == "USD"
        return self.points


def _points() -> list[RatePoint]:
    start = datetime(2026, 10, 12, tzinfo=UTC)
    return [
        RatePoint("USD", 100, start, "fixture"),
        RatePoint("USD", 101, start + timedelta(days=1), "fixture"),
        RatePoint("USD", 103, start + timedelta(days=2), "fixture"),
    ]


def test_analytics_engine_uses_only_rate_provider_contract() -> None:
    engine = AnalyticsEngine(InMemoryProvider(_points()))
    result = asyncio.run(engine.volatility("USD"))

    assert result.currency == "USD"
    assert result.observations == 3
    assert result.source == "fixture"
    assert result.daily_volatility_pct > 0


def test_buffer_is_positive_for_nonzero_volatility() -> None:
    engine = AnalyticsEngine(InMemoryProvider(_points()))
    result = asyncio.run(engine.buffer("USD", horizon_days=7, confidence=0.95))

    assert result.buffer_pct > 0
    assert result.buffered_rate > result.latest_rate


def test_volatility_requires_three_daily_observations() -> None:
    engine = AnalyticsEngine(InMemoryProvider(_points()[:2]))

    with pytest.raises(MissingRateHistory):
        asyncio.run(engine.volatility("USD"))