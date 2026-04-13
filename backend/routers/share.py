from fastapi import APIRouter

router = APIRouter(prefix="/api/share", tags=["share"])

@router.get("/card/{joke_id}")
async def get_share_card(joke_id: int):
    return {"message": "Card PNG generation coming soon"}
