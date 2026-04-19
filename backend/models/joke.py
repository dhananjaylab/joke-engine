from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, Integer, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from core.database import Base

# Valid source identifiers — extend this list as new integrations are added
JOKE_SOURCES = (
    "ai_generated",       # POST /api/jokes/generate  (OpenAI)
    "ai_streamed",        # GET  /api/jokes/stream  (SSE)
    "ai_websocket",       # WS   /ws/joke
    "api_ninjas_random",  # GET  /api/jokes/random  (API Ninjas /v1/jokes)
    "api_ninjas_daily",   # GET  /api/jokes/joke-of-the-day
)


class Joke(Base):
    __tablename__ = "jokes"

    id:                Mapped[int]           = mapped_column(primary_key=True, autoincrement=True)
    query:             Mapped[str]           = mapped_column(String(200), index=True)
    response:          Mapped[str]           = mapped_column(Text)
    source:            Mapped[str]           = mapped_column(String(40), default="ai_generated", index=True)
    session_key:       Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    created_at:        Mapped[datetime]      = mapped_column(DateTime, server_default=func.now())
    share_count:       Mapped[int]           = mapped_column(Integer, default=0)
    audio_url:         Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    score_originality: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    score_timing:      Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    score_cleverness:  Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    def __repr__(self):
        return f"<Joke id={self.id} source={self.source!r} query={self.query!r}>"
