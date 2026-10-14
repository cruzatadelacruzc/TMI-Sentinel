from datetime import UTC, datetime
from decimal import Decimal

import pytest

from app.core.base_repository import BaseRepository
from app.modules.eltoque.models import ElToqueRate


@pytest.mark.asyncio
async def test_generic_repository_crud_and_bulk_create(db_session) -> None:
    repository = BaseRepository(db_session, ElToqueRate)
    first = await repository.create(
        currency="USD",
        variant="default",
        rate=Decimal("100.00"),
        observed_at=datetime(2026, 10, 12, tzinfo=UTC),
    )
    second = await repository.create(
        currency="EUR",
        variant="default",
        rate=Decimal("110.00"),
        observed_at=datetime(2026, 10, 12, tzinfo=UTC),
    )

    assert first.id is not None
    assert first.created_at is not None
    assert first.updated_at is not None
    assert (await repository.get_by_id(first.id)).currency == "USD"
    assert len(await repository.list(limit=1)) == 1
    bulk_created = await repository.bulk_create(
        [
            {
                "currency": "CAD",
                "variant": "default",
                "rate": Decimal("75.00"),
                "observed_at": datetime(2026, 10, 12, tzinfo=UTC),
            }
        ]
    )
    assert len(bulk_created) == 1
    assert len(await repository.list(limit=10)) == 3
    assert await repository.get_by_id(second.id) is not None