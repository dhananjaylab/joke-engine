"""
joke_store.py — central joke persistence service.

Every joke that enters the system, regardless of origin, is saved through
`save_joke()`.  This guarantees:
  - A consistent DB record with source + session_key tracking
  - Background AI scoring enqueued automatically
  - Structured logging on every save

Supported sources (see models/joke.py JOKE_SOURCES):
    ai_generated       — POST /api/jokes/generate
    ai_streamed        — GET  /api/jokes/stream  (SSE)
    ai_websocket       — WS   /ws/joke
    api_ninjas_random  — GET  /api/jokes/random
    api_ninjas_daily   — GET  /api/jokes/joke-of-the-day  (mirror copy)
"""
from __future__ import annotations

import asyncio
import time
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from core.logging import get_logger
from models.joke import Joke

log = get_logger("services.joke_store")


async def save_joke(
    db: AsyncSession,
    *,
    query: str,
    response: str,
    source: str,
    session_key: Optional[str] = None,
    enqueue_scoring: bool = True,
) -> Joke:
    """
    Persist a joke to Neon PostgreSQL and optionally enqueue AI scoring.

    Parameters
    ----------
    db            : active async DB session
    query         : the topic / prompt string (will be stored as-is)
    response      : the joke text
    source        : one of JOKE_SOURCES — identifies the origin pipeline
    session_key   : user session UUID (nullable for system-generated jokes)
    enqueue_scoring: whether to kick off background AI scoring (default True)

    Returns
    -------
    The persisted Joke ORM instance (id is populated after flush).
    """
    start = time.perf_counter()

    joke = Joke(
        query=query,
        response=response,
        source=source,
        session_key=session_key,
    )
    db.add(joke)
    await db.flush()       # populate joke.id without committing
    await db.refresh(joke)
    await db.commit()

    duration_ms = int((time.perf_counter() - start) * 1000)
    await log.info(
        "joke_saved",
        f"Joke saved: id={joke.id} source={source!r} in {duration_ms}ms",
        joke_id=joke.id,
        session_key=session_key,
        duration_ms=duration_ms,
        details={
            "source": source,
            "query": query[:80],
            "response_length": len(response),
        },
    )

    if enqueue_scoring:
        asyncio.create_task(_enqueue_score(joke.id))

    return joke


# ---------------------------------------------------------------------------
# Internal — scoring enqueue (mirrors routers/jokes.py but lives here so
# every caller gets it for free without importing the router)
# ---------------------------------------------------------------------------

async def _enqueue_score(joke_id: int) -> None:
    from arq import create_pool
    from arq.connections import RedisSettings
    from core.config import get_settings
    from workers.fallback import score_joke_sync

    settings = get_settings()
    try:
        pool = await create_pool(RedisSettings.from_dsn(settings.redis_url))
        await pool.enqueue_job("task_score_joke", joke_id)
        await pool.close(close_connection_pool=True)
        await log.info(
            "score_enqueued",
            f"Scoring task enqueued for joke {joke_id}",
            joke_id=joke_id,
        )
    except Exception as exc:
        await log.warning(
            "score_enqueue_failed",
            f"ARQ enqueue failed for joke {joke_id} — using fallback",
            joke_id=joke_id,
            exc=exc,
        )
        asyncio.create_task(score_joke_sync(joke_id))
