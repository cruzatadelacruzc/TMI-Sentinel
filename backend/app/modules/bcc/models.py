from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, JSON, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base_model import Base


class BccRate(Base):
    __tablename__ = "bcc_rates"
    __table_args__ = (
        UniqueConstraint(
            "currency", "variant", "provider", "observed_at",
            name="uq_bcc_rate_provider_time",
        ),
    )

    currency: Mapped[str] = mapped_column(String(12), index=True)
    variant: Mapped[str] = mapped_column(String(64), default="default")
    provider: Mapped[str] = mapped_column(String(32), default="bcc")
    rate: Mapped[Decimal] = mapped_column(Numeric(18, 6))
    buy_rate: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))
    sell_rate: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    raw_payload: Mapped[dict | None] = mapped_column(JSON)