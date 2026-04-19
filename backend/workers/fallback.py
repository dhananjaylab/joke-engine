"""
Fallback scoring mechanism when ARQ worker is not available.
This allows the app to work without Redis/ARQ in development.
"""
import time
from core.database import AsyncSessionLocal
from core.logging import get_logger
from models.joke import Joke
from services.ai import score_joke
from sqlalchemy import select

log = get_logger("workers.fallback")


async def score_joke_sync(joke_id: int):
    """Score a joke synchronously (fallback when worker is unavailable)."""
    start = time.perf_counter()
    await log.info(
        "fallback_score_start",
        f"Fallback synchronous scoring started for joke {joke_id}",
        joke_id=joke_id,
    )

    try:
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(Joke).where(Joke.id == joke_id))
            joke = result.scalar_one_or_none()

            if not joke:
                await log.warning(
                    "fallback_score_joke_missing",
                    f"Joke {joke_id} not found — skipping fallback scoring",
                    joke_id=joke_id,
                )
                return

            scores = await score_joke(joke.response)
            if not scores:
                await log.warning(
                    "fallback_score_empty",
                    f"AI returned empty scores for joke {joke_id} (fallback)",
                    joke_id=joke_id,
                )
                return

            joke.score_originality = scores.get("originality")
            joke.score_timing = scores.get("timing")
            joke.score_cleverness = scores.get("cleverness")
            await db.commit()

            duration_ms = int((time.perf_counter() - start) * 1000)
            await log.info(
                "fallback_score_complete",
                f"Joke {joke_id} scored via fallback in {duration_ms}ms: {scores}",
                joke_id=joke_id,
                duration_ms=duration_ms,
                details={"scores": scores},
            )

    except Exception as exc:
        duration_ms = int((time.perf_counter() - start) * 1000)
        await log.error(
            "fallback_score_failed",
            f"Fallback scoring failed for joke {joke_id}",
            joke_id=joke_id,
            duration_ms=duration_ms,
            exc=exc,
        )
