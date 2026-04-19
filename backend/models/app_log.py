"""
AppLog model — persists structured log entries to Neon PostgreSQL.
Every major process in the application writes a record here.
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, DateTime, Integer, JSON, func, Index
from sqlalchemy.orm import Mapped, mapped_column
from core.database import Base


class AppLog(Base):
    """
    Structured application log stored in PostgreSQL.

    Fields
    ------
    id          : auto-increment PK
    level       : DEBUG / INFO / WARNING / ERROR / CRITICAL
    logger_name : dotted module path (e.g. "services.ai", "workers.tasks")
    event       : short machine-readable event key (e.g. "joke_generated")
    message     : human-readable description
    details     : arbitrary JSON payload (request params, scores, durations …)
    session_key : user session UUID (nullable — not all events are user-scoped)
    joke_id     : FK-like reference to jokes.id (nullable)
    duration_ms : elapsed time in milliseconds (nullable)
    error       : exception class + message (nullable)
    traceback   : full traceback string (nullable)
    created_at  : UTC timestamp (server default)
    """

    __tablename__ = "app_logs"

    id:           Mapped[int]            = mapped_column(Integer, primary_key=True, autoincrement=True)
    level:        Mapped[str]            = mapped_column(String(10), nullable=False, index=True)
    logger_name:  Mapped[str]            = mapped_column(String(120), nullable=False, index=True)
    event:        Mapped[str]            = mapped_column(String(80), nullable=False, index=True)
    message:      Mapped[str]            = mapped_column(Text, nullable=False)
    details:      Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    session_key:  Mapped[Optional[str]]  = mapped_column(String(64), nullable=True, index=True)
    joke_id:      Mapped[Optional[int]]  = mapped_column(Integer, nullable=True, index=True)
    duration_ms:  Mapped[Optional[int]]  = mapped_column(Integer, nullable=True)
    error:        Mapped[Optional[str]]  = mapped_column(Text, nullable=True)
    traceback:    Mapped[Optional[str]]  = mapped_column(Text, nullable=True)
    created_at:   Mapped[datetime]       = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )

    __table_args__ = (
        # Composite index for the most common query pattern: level + time range
        Index("ix_app_logs_level_created", "level", "created_at"),
        # Composite index for per-event analytics
        Index("ix_app_logs_event_created", "event", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<AppLog id={self.id} level={self.level} event={self.event}>"
