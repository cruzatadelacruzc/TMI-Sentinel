from datetime import datetime
from typing import Any, Generic, Mapping, Sequence, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.base_model import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, session: AsyncSession, model: type[ModelType]) -> None:
        self.session = session
        self.model = model

    async def create(self, **values: Any) -> ModelType:
        record = self.model(**values)
        self.session.add(record)
        await self.session.commit()
        await self.session.refresh(record)
        return record

    async def get_by_id(self, record_id: int) -> ModelType | None:
        return await self.session.get(self.model, record_id)

    async def list(self, offset: int = 0, limit: int = 100) -> list[ModelType]:
        statement = select(self.model).offset(offset).limit(limit)
        result = await self.session.scalars(statement)
        return list(result)

    async def bulk_create(
        self, records: Sequence[Mapping[str, Any]]
    ) -> list[ModelType]:
        created = [self.model(**values) for values in records]
        if not created:
            return []
        self.session.add_all(created)
        await self.session.commit()
        for record in created:
            await self.session.refresh(record)
        return created

    async def list_range(
        self,
        currency: str,
        start: datetime | None = None,
        end: datetime | None = None,
        variant: str | None = None,
        provider: str | None = None,
    ) -> list[ModelType]:
        statement = select(self.model).where(self.model.currency == currency)
        if variant is not None and hasattr(self.model, "variant"):
            statement = statement.where(self.model.variant == variant)
        if provider is not None and hasattr(self.model, "provider"):
            statement = statement.where(self.model.provider == provider)
        if start is not None:
            statement = statement.where(self.model.observed_at >= start)
        if end is not None:
            statement = statement.where(self.model.observed_at <= end)
        statement = statement.order_by(self.model.observed_at)
        result = await self.session.scalars(statement)
        return list(result)