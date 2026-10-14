from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

router = APIRouter()


class SchedulerUpdate(BaseModel):
    interval_minutes: int | None = Field(default=None, ge=1, le=10080)
    enabled: bool | None = None


@router.get("")
async def scheduler_status(request: Request) -> dict:
    manager = request.app.state.scheduler_manager
    if manager is None:
        raise HTTPException(status_code=503, detail="Scheduler requires DATABASE_URL")
    return manager.status()


@router.put("")
async def update_scheduler(
    update: SchedulerUpdate, request: Request
) -> dict:
    manager = request.app.state.scheduler_manager
    if manager is None:
        raise HTTPException(status_code=503, detail="Scheduler requires DATABASE_URL")
    return await manager.update(
        interval_minutes=update.interval_minutes,
        enabled=update.enabled,
    )