from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, Integer, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from core.database import Base


class Joke(Base):
    __tablename__ = "jokes"

    id:               Mapped[int]            = mapped_column(primary_key=True, autoincrement=True)
    query:            Mapped[str]            = mapped_column(String(100), index=True)
    response:         Mapped[str]            = mapped_column(Text)
    created_at:       Mapped[datetime]       = mapped_column(DateTime, server_default=func.now())
    share_count:      Mapped[int]            = mapped_column(Integer, default=0)
    audio_url:        Mapped[Optional[str]]  = mapped_column(Text, nullable=True)
    score_originality: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    score_timing:     Mapped[Optional[int]]  = mapped_column(Integer, nullable=True)
    score_cleverness: Mapped[Optional[int]]  = mapped_column(Integer, nullable=True)

    def __repr__(self):
        return f"<Joke id={self.id} query={self.query!r}>"
