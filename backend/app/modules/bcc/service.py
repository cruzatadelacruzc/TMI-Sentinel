from datetime import datetime
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ProviderError
from app.core.rate_provider import RatePoint, RateProvider
from app.modules.bcc.client import BccClient
from app.modules.bcc.fallback import BccFallbackClient
from app.modules.bcc.repository import BccRepository

logger = logging.getLogger(__name__)


class BccService(RateProvider):
    def __init__(
        self,
        session: AsyncSession,
        client: BccClient,
        fallback_client: BccFallbackClient | None = None,
    ) -> None:
        self.repository = BccRepository(session)
        self.client = client
        self.fallback_client = fallback_client

    async def ingest(self) -> int:
        try:
            rates = await self.client.fetch_rates()
        except ProviderError:
            if self.fallback_client is None:
                raise
            logger.exception("BCC widget failed; trying configured fallback")
            rates = await self.fallback_client.fetch_rates()
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
            currency.upper(), start, end, variant=variant, provider=source or "bcc"
        )
        return [
            RatePoint(
                currency=record.currency,
                rate=float(record.rate),
                observed_at=record.observed_at,
                source=record.provider,
                variant=record.variant,
                buy_rate=float(record.buy_rate) if record.buy_rate else None,
                sell_rate=float(record.sell_rate) if record.sell_rate else None,
            )
            for record in records
        ]