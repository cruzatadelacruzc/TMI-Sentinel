import logging

from sqlalchemy.ext.asyncio import async_sessionmaker

from app.config import Settings
from app.modules.bcc.client import BccClient
from app.modules.bcc.fallback import BccFallbackClient
from app.modules.bcc.service import BccService
from app.modules.eltoque.client import ElToqueClient
from app.modules.eltoque.service import ElToqueService

logger = logging.getLogger(__name__)


async def ingest_all(
    session_factory: async_sessionmaker,
    settings: Settings,
) -> dict[str, int | str]:
    outcomes: dict[str, int | str] = {}
    async with session_factory() as session:
        providers = {
            "eltoque": ElToqueService(session, ElToqueClient(settings)),
            "bcc": BccService(
                session,
                BccClient(settings),
                BccFallbackClient(settings)
                if settings.bcc_fallback_api_url
                else None,
            ),
        }
        for name, provider in providers.items():
            try:
                outcomes[name] = await provider.ingest()
            except Exception as exc:
                logger.exception("Scheduled %s ingestion failed", name)
                outcomes[name] = str(exc)
    return outcomes