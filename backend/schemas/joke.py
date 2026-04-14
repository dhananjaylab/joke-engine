from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class GenerateRequest(BaseModel):
    query: str
    style: str = "witty"
    regenerate: bool = False


class JokeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    query: str
    response: str
    created_at: datetime
    share_count: int
    audio_url: Optional[str]
    score_originality: Optional[int]
    score_timing: Optional[int]
    score_cleverness: Optional[int]


class PaginatedJokes(BaseModel):
    jokes: list[JokeResponse]
    total: int
    page: int
    pages: int


class HeckleRequest(BaseModel):
    joke: str


class HeckleResponse(BaseModel):
    rating: str
    roast: str
