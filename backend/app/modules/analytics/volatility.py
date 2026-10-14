import math
import statistics
from datetime import UTC

from app.core.exceptions import MissingRateHistory
from app.core.rate_provider import RatePoint


def daily_observations(points: list[RatePoint]) -> list[RatePoint]:
    by_day = {}
    for point in points:
        day = point.observed_at.astimezone(UTC).date()
        previous = by_day.get(day)
        if previous is None or point.observed_at > previous.observed_at:
            by_day[day] = point
    return [by_day[day] for day in sorted(by_day)]


def calculate_daily_volatility(points: list[RatePoint]) -> float:
    observations = daily_observations(points)
    if len(observations) < 3:
        raise MissingRateHistory("At least three distinct days of rates are required")
    returns = [
        math.log(current.rate / previous.rate) * 100
        for previous, current in zip(observations, observations[1:])
        if previous.rate > 0 and current.rate > 0
    ]
    if not returns:
        raise MissingRateHistory("No valid daily rate changes are available")
    return statistics.pstdev(returns)