from fastapi import APIRouter

router = APIRouter(prefix="/api/battle", tags=["battle"])

@router.get("/")
async def list_battles():
    return []
