from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.base_repository import BaseRepository
from app.core.rate_provider import RatePoint
from app.modules.bcc.models import BccRate


class BccRepository(BaseRepository[BccRate]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, BccRate)

    async def save_many(self, rates: list[RatePoint]) -> int:
        saved = 0
        for point in rates:
            statement = select(BccRate).where(
                BccRate.currency == point.currency,
                BccRate.variant == point.variant,
                BccRate.provider == point.source,
                BccRate.observed_at == point.observed_at,
            )
            existing = await self.session.scalar(statement)
            values = {
                "rate": Decimal(str(point.rate)),
                "buy_rate": (
                    Decimal(str(point.buy_rate))
                    if point.buy_rate is not None
                    else None
                ),
                "sell_rate": (
                    Decimal(str(point.sell_rate))
                    if point.sell_rate is not None
                    else None
                ),
            }
            if existing is None:
                self.session.add(
                    BccRate(
                        currency=point.currency,
                        variant=point.variant,
                        provider=point.source,
                        observed_at=point.observed_at,
                        **values,
                    )
                )
            else:
                for key, value in values.items():
                    setattr(existing, key, value)
            saved += 1
        await self.session.commit()
        return saved