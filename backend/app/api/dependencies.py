from fastapi import HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rate_provider import RateProvider
from app.modules.bcc.client import BccClient
from app.modules.bcc.fallback import BccFallbackClient
from app.modules.bcc.service import BccService
from app.modules.eltoque.client import ElToqueClient
from app.modules.eltoque.service import ElToqueService


def create_provider(
    source: str, session: AsyncSession, request: Request
) -> RateProvider:
    settings = request.app.state.settings
    if source == "eltoque":
        return ElToqueService(session, ElToqueClient(settings))
    if source in {"bcc", "bcc_fallback"}:
        return BccService(
            session,
            BccClient(settings),
            BccFallbackClient(settings)
            if settings.bcc_fallback_api_url
            else None,
        )
    raise HTTPException(
        status_code=422,
        detail="source must be 'eltoque', 'bcc', or 'bcc_fallback'",
    )