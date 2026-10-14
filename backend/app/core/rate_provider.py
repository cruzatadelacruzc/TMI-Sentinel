from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


@dataclass(frozen=True)
class RatePoint:
    currency: str
    rate: float
    observed_at: datetime
    source: str
    variant: str = "default"
    buy_rate: float | None = None
    sell_rate: float | None = None


class RateProvider(Protocol):
    async def get_history(
        self,
        currency: str,
        start: datetime | None = None,
        end: datetime | None = None,
        variant: str | None = None,
        source: str | None = None,
    ) -> list[RatePoint]: ...