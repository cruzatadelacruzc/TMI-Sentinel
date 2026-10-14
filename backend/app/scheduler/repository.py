from app.scheduler.models import SchedulerSettings
from sqlalchemy.ext.asyncio import AsyncSession


class SchedulerRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self) -> SchedulerSettings | None:
        return await self.session.get(SchedulerSettings, 1)

    async def set(self, interval_minutes: int, enabled: bool) -> SchedulerSettings:
        current = await self.get()
        if current is None:
            current = SchedulerSettings(
                interval_minutes=interval_minutes,
                enabled=enabled,
            )
            self.session.add(current)
        else:
            current.interval_minutes = interval_minutes
            current.enabled = enabled
        await self.session.commit()
        await self.session.refresh(current)
        return current