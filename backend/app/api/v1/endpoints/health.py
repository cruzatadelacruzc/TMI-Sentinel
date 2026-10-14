from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/health")
async def health(request: Request) -> dict[str, str]:
    database_state = "configured" if request.app.state.database.engine else "missing"
    return {"status": "ok", "database": database_state}