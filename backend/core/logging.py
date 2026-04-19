"""
Production logging system for Giggle API.

Architecture
------------
1. DBLogHandler  — Python logging.Handler that writes AppLog rows to Neon PostgreSQL
                   via a background asyncio queue (fire-and-forget, never blocks the
                   request path).
2. AppLogger     — Thin async helper that wraps the standard logger and provides
                   structured, event-keyed log methods used throughout the codebase.
3. get_logger()  — Factory that returns an AppLogger bound to a module name.
4. setup_logging() — Called once at startup; configures root logger, console handler,
                     and starts the DB flush loop.

Usage
-----
    from core.logging import get_logger
    log = get_logger(__name__)

    # Simple info
    await log.info("joke_generated", "New joke saved", joke_id=42, duration_ms=310)

    # Error with exception
    try:
        ...
    except Exception as exc:
        await log.error("ai_call_failed", "OpenAI request failed", exc=exc)
"""

from __future__ import annotations

import asyncio
import logging
import sys
import traceback
from datetime import datetime, timezone
from typing import Any, Optional

# ---------------------------------------------------------------------------
# Standard Python logging setup (console)
# ---------------------------------------------------------------------------

LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

_LEVEL_MAP: dict[str, int] = {
    "DEBUG":    logging.DEBUG,
    "INFO":     logging.INFO,
    "WARNING":  logging.WARNING,
    "ERROR":    logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}


def setup_logging(log_level: str = "INFO") -> None:
    """
    Configure root logger with a console handler.
    Call once at application startup (main.py lifespan).
    """
    level = _LEVEL_MAP.get(log_level.upper(), logging.INFO)

    root = logging.getLogger()
    root.setLevel(level)

    # Avoid duplicate handlers if called more than once
    if not any(isinstance(h, logging.StreamHandler) for h in root.handlers):
        console = logging.StreamHandler(sys.stdout)
        console.setLevel(level)
        console.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))
        root.addHandler(console)

    # Quieten noisy third-party loggers
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("arq").setLevel(logging.INFO)
    logging.getLogger("apscheduler").setLevel(logging.INFO)


# ---------------------------------------------------------------------------
# Async DB log queue
# ---------------------------------------------------------------------------

_log_queue: asyncio.Queue[dict[str, Any]] | None = None
_flush_task: asyncio.Task | None = None


def _get_queue() -> asyncio.Queue[dict[str, Any]]:
    global _log_queue
    if _log_queue is None:
        _log_queue = asyncio.Queue(maxsize=2000)
    return _log_queue


async def _flush_loop() -> None:
    """
    Background coroutine that drains the log queue and bulk-inserts into
    the app_logs table.  Runs for the lifetime of the application.
    """
    from core.database import AsyncSessionLocal
    from models.app_log import AppLog

    queue = _get_queue()
    logger = logging.getLogger("core.logging")

    while True:
        # Collect up to 50 entries or wait up to 2 seconds
        batch: list[dict[str, Any]] = []
        try:
            entry = await asyncio.wait_for(queue.get(), timeout=2.0)
            batch.append(entry)
            # Drain any additional items already in the queue
            while not queue.empty() and len(batch) < 50:
                batch.append(queue.get_nowait())
        except asyncio.TimeoutError:
            pass  # Nothing in queue — loop again

        if not batch:
            continue

        try:
            async with AsyncSessionLocal() as db:
                db.add_all([AppLog(**entry) for entry in batch])
                await db.commit()
        except Exception as exc:
            # Never let DB errors crash the flush loop; fall back to stderr
            logger.warning(
                "DB log flush failed (%s) — %d entries dropped to stderr",
                exc,
                len(batch),
            )
            for entry in batch:
                logger.warning("DROPPED LOG: %s", entry)


def start_db_log_flush() -> None:
    """Start the background flush loop.  Call from lifespan startup."""
    global _flush_task
    if _flush_task is None or _flush_task.done():
        _flush_task = asyncio.create_task(_flush_loop(), name="db-log-flush")


def stop_db_log_flush() -> None:
    """Cancel the flush loop.  Call from lifespan shutdown."""
    global _flush_task
    if _flush_task and not _flush_task.done():
        _flush_task.cancel()


# ---------------------------------------------------------------------------
# AppLogger — structured async logger
# ---------------------------------------------------------------------------

class AppLogger:
    """
    Structured logger that writes to both the Python logging system (console)
    and the Neon PostgreSQL app_logs table via the async queue.
    """

    def __init__(self, name: str) -> None:
        self._name = name
        self._py_logger = logging.getLogger(name)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _enqueue(
        self,
        level: str,
        event: str,
        message: str,
        *,
        details: Optional[dict] = None,
        session_key: Optional[str] = None,
        joke_id: Optional[int] = None,
        duration_ms: Optional[int] = None,
        exc: Optional[BaseException] = None,
    ) -> None:
        """Push a log entry onto the async queue (non-blocking)."""
        error_str: Optional[str] = None
        tb_str: Optional[str] = None

        if exc is not None:
            error_str = f"{type(exc).__name__}: {exc}"
            tb_str = traceback.format_exc()

        entry: dict[str, Any] = {
            "level":       level,
            "logger_name": self._name,
            "event":       event,
            "message":     message,
            "details":     details,
            "session_key": session_key,
            "joke_id":     joke_id,
            "duration_ms": duration_ms,
            "error":       error_str,
            "traceback":   tb_str,
        }

        try:
            queue = _get_queue()
            queue.put_nowait(entry)
        except asyncio.QueueFull:
            # Queue is full — log to stderr only, never block
            self._py_logger.warning(
                "Log queue full — entry dropped: event=%s message=%s", event, message
            )

    def _py_log(self, level: int, event: str, message: str, exc: Optional[BaseException]) -> None:
        """Mirror the entry to the Python (console) logger."""
        extra_msg = f"[{event}] {message}"
        if exc:
            self._py_logger.log(level, extra_msg, exc_info=exc)
        else:
            self._py_logger.log(level, extra_msg)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def debug(
        self,
        event: str,
        message: str,
        *,
        details: Optional[dict] = None,
        session_key: Optional[str] = None,
        joke_id: Optional[int] = None,
        duration_ms: Optional[int] = None,
    ) -> None:
        self._py_log(logging.DEBUG, event, message, None)
        self._enqueue(
            "DEBUG", event, message,
            details=details, session_key=session_key,
            joke_id=joke_id, duration_ms=duration_ms,
        )

    async def info(
        self,
        event: str,
        message: str,
        *,
        details: Optional[dict] = None,
        session_key: Optional[str] = None,
        joke_id: Optional[int] = None,
        duration_ms: Optional[int] = None,
    ) -> None:
        self._py_log(logging.INFO, event, message, None)
        self._enqueue(
            "INFO", event, message,
            details=details, session_key=session_key,
            joke_id=joke_id, duration_ms=duration_ms,
        )

    async def warning(
        self,
        event: str,
        message: str,
        *,
        details: Optional[dict] = None,
        session_key: Optional[str] = None,
        joke_id: Optional[int] = None,
        duration_ms: Optional[int] = None,
        exc: Optional[BaseException] = None,
    ) -> None:
        self._py_log(logging.WARNING, event, message, exc)
        self._enqueue(
            "WARNING", event, message,
            details=details, session_key=session_key,
            joke_id=joke_id, duration_ms=duration_ms, exc=exc,
        )

    async def error(
        self,
        event: str,
        message: str,
        *,
        details: Optional[dict] = None,
        session_key: Optional[str] = None,
        joke_id: Optional[int] = None,
        duration_ms: Optional[int] = None,
        exc: Optional[BaseException] = None,
    ) -> None:
        self._py_log(logging.ERROR, event, message, exc)
        self._enqueue(
            "ERROR", event, message,
            details=details, session_key=session_key,
            joke_id=joke_id, duration_ms=duration_ms, exc=exc,
        )

    async def critical(
        self,
        event: str,
        message: str,
        *,
        details: Optional[dict] = None,
        session_key: Optional[str] = None,
        joke_id: Optional[int] = None,
        duration_ms: Optional[int] = None,
        exc: Optional[BaseException] = None,
    ) -> None:
        self._py_log(logging.CRITICAL, event, message, exc)
        self._enqueue(
            "CRITICAL", event, message,
            details=details, session_key=session_key,
            joke_id=joke_id, duration_ms=duration_ms, exc=exc,
        )


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def get_logger(name: str) -> AppLogger:
    """Return an AppLogger bound to *name* (typically __name__)."""
    return AppLogger(name)
