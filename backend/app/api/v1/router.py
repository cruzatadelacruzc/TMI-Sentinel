from fastapi import APIRouter

from app.api.v1.endpoints import analytics, bcc, eltoque, health, scheduler

router = APIRouter()
router.include_router(health.router, tags=["health"])
router.include_router(eltoque.router, prefix="/eltoque", tags=["eltoque"])
router.include_router(bcc.router, prefix="/bcc", tags=["bcc"])
router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
router.include_router(scheduler.router, prefix="/scheduler", tags=["scheduler"])