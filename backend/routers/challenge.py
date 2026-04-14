from fastapi import APIRouter

router = APIRouter(prefix="/api/challenge", tags=["challenge"])

@router.get("/")
async def get_current_challenge():
    return {"challenge": "Weekly roast of the latest tech news"}
