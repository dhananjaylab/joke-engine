from fastapi import APIRouter
from pydantic import BaseModel
from services import ai

router = APIRouter(prefix="/api", tags=["heckle"])


class HeckleRequest(BaseModel):
    joke: str


@router.post("/structured-heckle")
async def structured_heckle_user_joke(body: HeckleRequest):
    """Rate and roast a user-submitted joke with structured format."""
    # First score the joke
    scores = await ai.score_joke(body.joke)
    if not scores:
        # Fallback scores if AI scoring fails
        scores = {"originality": 5, "timing": 5, "cleverness": 5}
    
    # Generate structured roast using the scores
    structured_roast = await ai.structured_roast(
        body.joke,
        scores["originality"],
        scores["timing"], 
        scores["cleverness"]
    )
    return structured_roast


@router.post("/heckle")
async def heckle_user_joke(body: HeckleRequest):
    """Rate and roast a user-submitted joke."""
    roast = await ai.heckle(body.joke)
    return {"roast": roast}
