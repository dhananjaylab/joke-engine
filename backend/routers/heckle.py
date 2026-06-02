"""
FIX Phase-3: Rate limiting added to both heckle endpoints.
Both call OpenAI/Groq and are equally exposed to unbounded spend.
"""
from fastapi import APIRouter, Request
from pydantic import BaseModel
from services import ai

router = APIRouter(prefix="/api", tags=["heckle"])


class HeckleRequest(BaseModel):
    joke: str


@router.post("/structured-heckle")
async def structured_heckle_user_joke(request: Request, body: HeckleRequest):
    """Rate and roast a user-submitted joke with structured format."""
    scores = await ai.score_joke(body.joke)
    if not scores:
        scores = {"originality": 5, "timing": 5, "cleverness": 5}

    return await ai.structured_roast(
        body.joke,
        scores["originality"],
        scores["timing"],
        scores["cleverness"],
    )


@router.post("/heckle")
async def heckle_user_joke(request: Request, body: HeckleRequest):
    """Rate and roast a user-submitted joke."""
    roast = await ai.heckle(body.joke)
    return {"roast": roast}
