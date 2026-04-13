from datetime import date, datetime
from typing import Optional
from sqlalchemy import String, Integer, Date, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from core.database import Base

RANK_THRESHOLDS = [
    (1000, "GOAT"),
    (400,  "Legend"),
    (150,  "Headliner"),
    (50,   "Club Regular"),
    (0,    "Open Mic"),
]


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id:           Mapped[int]           = mapped_column(primary_key=True)
    session_key:  Mapped[str]           = mapped_column(String(64), unique=True, index=True)
    xp:           Mapped[int]           = mapped_column(Integer, default=0)
    streak:       Mapped[int]           = mapped_column(Integer, default=0)
    last_visit:   Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    created_at:   Mapped[datetime]      = mapped_column(DateTime, server_default=func.now())

    @property
    def rank(self) -> str:
        for threshold, label in RANK_THRESHOLDS:
            if self.xp >= threshold:
                return label
        return "Open Mic"

    def __repr__(self):
        return f"<UserProfile session_key={self.session_key} xp={self.xp}>"
