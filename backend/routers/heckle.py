from fastapi import APIRouter
from pydantic import BaseModel
from services.ai import heckle

router = APIRouter(prefix="/api", tags=["heckle"])


class HeckleRequest(BaseModel):
    joke: str


@router.post("/heckle")
async def heckle_user_joke(body: HeckleRequest):
    """Rate and roast a user-submitted joke."""
    roast = await heckle(body.joke)
    return {"roast": roast}
