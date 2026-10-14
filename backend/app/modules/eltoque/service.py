from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rate_provider import RatePoint, RateProvider
from app.modules.eltoque.client import ElToqueClient
from app.modules.eltoque.repository import ElToqueRepository


class ElToqueService(RateProvider):
    def __init__(self, session: AsyncSession, client: ElToqueClient) -> None:
        self.repository = ElToqueRepository(session)
        self.client = client

    async def ingest(self) -> int:
        rates = await self.client.fetch_rates()
        return await self.repository.save_many(rates)

    async def get_history(
        self,
        currency: str,
        start: datetime | None = None,
        end: datetime | None = None,
        variant: str | None = None,
        source: str | None = None,
    ) -> list[RatePoint]:
        records = await self.repository.list_range(
            currency.upper(), start, end, variant=variant
        )
        return [
            RatePoint(
                currency=record.currency,
                rate=float(record.rate),
                observed_at=record.observed_at,
                source="eltoque",
                variant=record.variant,
                buy_rate=float(record.buy_rate) if record.buy_rate else None,
                sell_rate=float(record.sell_rate) if record.sell_rate else None,
            )
            for record in records
        ]