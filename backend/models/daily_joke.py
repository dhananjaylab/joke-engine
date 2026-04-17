from datetime import date
from sqlalchemy import String, Text, Date
from sqlalchemy.orm import Mapped, mapped_column
from core.database import Base


class DailyJoke(Base):
    """Stores the joke of the day, fetched once per day from API Ninjas."""
    __tablename__ = "daily_jokes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    joke_date: Mapped[date] = mapped_column(Date, unique=True, index=True)
    joke_text: Mapped[str] = mapped_column(Text)
    source: Mapped[str] = mapped_column(String(50), default="api_ninjas")

    def __repr__(self):
        return f"<DailyJoke date={self.joke_date} source={self.source}>"
