import logging
from typing import Any

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.config import Settings
from app.scheduler.config import resolve_interval
from app.scheduler.jobs import ingest_all
from app.scheduler.repository import SchedulerRepository

logger = logging.getLogger(__name__)


class SchedulerManager:
    def __init__(
        self,
        settings: Settings,
        session_factory: async_sessionmaker,
    ) -> None:
        self.settings = settings
        self.session_factory = session_factory
        self.scheduler = AsyncIOScheduler(timezone="UTC")
        self.interval_minutes = settings.scheduler_interval_minutes or 60
        self.enabled = settings.scheduler_enabled

    async def configure(self) -> None:
        async with self.session_factory() as session:
            stored = await SchedulerRepository(session).get()
            stored_interval = stored.interval_minutes if stored else None
            self.enabled = stored.enabled if stored else self.settings.scheduler_enabled
        self.interval_minutes = resolve_interval(
            self.settings.scheduler_interval_minutes, stored_interval
        )
        self._configure_job()
        if self.enabled:
            self.scheduler.start()
        logger.info(
            "Scheduler configured",
            extra={"enabled": self.enabled, "interval_minutes": self.interval_minutes},
        )

    def _configure_job(self) -> None:
        self.scheduler.add_job(
            ingest_all,
            trigger=IntervalTrigger(minutes=self.interval_minutes, timezone="UTC"),
            args=[self.session_factory, self.settings],
            id="ingest_exchange_rates",
            replace_existing=True,
            max_instances=1,
            coalesce=True,
        )

    async def update(
        self, interval_minutes: int | None = None, enabled: bool | None = None
    ) -> dict[str, Any]:
        requested_interval = interval_minutes or self.interval_minutes
        requested_enabled = self.enabled if enabled is None else enabled
        async with self.session_factory() as session:
            await SchedulerRepository(session).set(
                requested_interval, requested_enabled
            )
        self.interval_minutes = resolve_interval(
            self.settings.scheduler_interval_minutes, requested_interval
        )
        self.enabled = requested_enabled
        if self.scheduler.running:
            self.scheduler.pause()
            self._configure_job()
            if self.enabled:
                self.scheduler.resume()
        elif self.enabled:
            self._configure_job()
            self.scheduler.start()
        return self.status()

    def status(self) -> dict[str, Any]:
        job = self.scheduler.get_job("ingest_exchange_rates")
        return {
            "enabled": self.enabled,
            "running": self.scheduler.running and self.enabled,
            "interval_minutes": self.interval_minutes,
            "next_run_time": job.next_run_time if job and self.enabled else None,
            "environment_interval_override": self.settings.scheduler_interval_minutes,
        }

    async def shutdown(self) -> None:
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)