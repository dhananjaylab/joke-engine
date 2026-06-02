"""
Central joke persistence service — all fixes applied.

FIXES:
  Phase-2a: Singleton ARQ pool — no longer creates a new pool per job.
  Phase-2b: Removed redundant db.refresh() after db.flush().
  Phase-2c: Normalise query to lowercase at write time so cache lookups
            can use a plain equality check and hit the ix_jokes_query index.
  Phase-3:  Added auto_commit parameter so callers can wrap the joke save
            and follow-up mutations (e.g. XP update) in a single transaction.
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
    auto_commit: bool = True,          # FIX Phase-3: caller controls transaction
) -> Joke:
    """
    Persist a joke to PostgreSQL and optionally enqueue AI scoring.

    Parameters
    ----------
    db            : active async DB session
    query         : the topic / prompt string — stored lower-cased (Phase-2c)
    response      : the joke text
    source        : one of JOKE_SOURCES
    session_key   : user session UUID (nullable)
    enqueue_scoring: whether to kick off background AI scoring
    auto_commit   : if False the caller is responsible for committing, allowing
                    joke + follow-up mutations to land in a single transaction

    Returns
    -------
    The persisted Joke ORM instance (id populated after flush).
    """
    start = time.perf_counter()

    # FIX Phase-2c: normalise once at write time so cache lookups can use
    # plain equality and hit the index instead of calling func.lower().
    normalised_query = query.lower().strip()

    joke = Joke(
        query=normalised_query,
        response=response,
        source=source,
        session_key=session_key,
    )
    db.add(joke)
    await db.flush()          # FIX Phase-2b: flush populates joke.id
    # refresh() REMOVED — it was an extra SELECT with no benefit here

    if auto_commit:
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
            "query": normalised_query[:80],
            "response_length": len(response),
            "auto_commit": auto_commit,
        },
    )

    if enqueue_scoring:
        asyncio.create_task(_enqueue_score(joke.id))

    return joke


# ---------------------------------------------------------------------------
# Internal — scoring enqueue (singleton pool, Phase-2a)
# ---------------------------------------------------------------------------

async def _enqueue_score(joke_id: int) -> None:
    # FIX Phase-2a: use the singleton pool instead of creating one per job.
    from workers.redis_client import get_arq_pool
    from workers.fallback import score_joke_sync

    try:
        pool = await get_arq_pool()
        await pool.enqueue_job("task_score_joke", joke_id)
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
