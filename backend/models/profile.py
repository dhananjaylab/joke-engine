from datetime import datetime
from sqlalchemy import String, Integer, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from core.database import Base


class UserProfile(Base):
    __tablename__ = "profiles"

    id:             Mapped[str]      = mapped_column(String(64), primary_key=True)  # Session ID or User ID
    xp:             Mapped[int]      = mapped_column(Integer, default=0)
    streak_count:   Mapped[int]      = mapped_column(Integer, default=0)
    last_active:    Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    created_at:     Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<UserProfile id={self.id} xp={self.xp}>"
