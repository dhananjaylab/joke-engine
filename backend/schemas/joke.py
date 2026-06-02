"""
FIX Phase-1: style field is now a Literal type — FastAPI validates and
rejects unknown values at the request boundary, and the generated OpenAPI
schema documents all valid options.

FIX Phase-4: PaginatedJokes now supports cursor-based pagination via
next_cursor instead of page/pages, enabling O(log n) history fetches.
"""
from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict

# All valid style identifiers — must be kept in sync with PERSONAS in services/ai.py
StyleType = Literal[
    "witty",
    "dad",
    "sarcastic",
    "roast",
    "haiku",
    "brainrot",
    "nocontext",
    "emoji",
    "observational",
    "dark",
    "gen-z",
    "millennial",
    "boomer",
    "meme",
    "tiktok",
    "twitter",
    "karen",
    "chad",
    "nerd",
    "hipster",
    "influencer",
    "corporate",
    "absurd",
    "puns",
    "self-deprecating",
    "wholesome",
    "cringe",
    "deadpan",
    "netflix",
    "gaming",
    "crypto",
    "fitness",
    "foodie",
    "travel",
]


class GenerateRequest(BaseModel):
    query: str
    style: StyleType = "witty"   # FIX: was `str`, now validated Literal
    regenerate: bool = False


class JokeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    query: str
    response: str
    source: str
    session_key: Optional[str]
    created_at: datetime
    share_count: int
    audio_url: Optional[str]
    score_originality: Optional[int]
    score_timing: Optional[int]
    score_cleverness: Optional[int]


class PaginatedJokes(BaseModel):
    """
    FIX Phase-4: cursor-based pagination replaces page/pages.

    Clients pass `cursor` (the last seen joke ID) on subsequent requests.
    `next_cursor` is None when there are no more results.
    """
    jokes: list[JokeResponse]
    total: int                       # total count (for display, not pagination)
    next_cursor: Optional[int]       # pass as ?cursor= on next request
    # Kept for backwards-compatibility during migration
    page: int = 1
    pages: int = 1


class HeckleRequest(BaseModel):
    joke: str


class HeckleResponse(BaseModel):
    rating: str
    roast: str
