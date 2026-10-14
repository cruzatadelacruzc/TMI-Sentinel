from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class ElToqueRateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    currency: str
    variant: str
    rate: Decimal
    buy_rate: Decimal | None
    sell_rate: Decimal | None
    observed_at: datetime