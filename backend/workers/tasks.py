"""ARQ task definitions. Run worker with: arq workers.settings.WorkerSettings"""
import time
from core.database import AsyncSessionLocal
from core.logging import get_logger
from models.joke import Joke
from services.ai import score_joke
from sqlalchemy import select

log = get_logger("workers.tasks")


async def task_score_joke(ctx, joke_id: int):
    """Background task: score a joke on 3 dimensions."""
    start = time.perf_counter()
    await log.info(
        "worker_score_start",
        f"Background scoring started for joke {joke_id}",
        joke_id=joke_id,
        details={"job_id": ctx.get("job_id") if ctx else None},
    )

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Joke).where(Joke.id == joke_id))
        joke = result.scalar_one_or_none()

        if not joke:
            await log.warning(
                "worker_score_joke_missing",
                f"Joke {joke_id} not found in DB — skipping scoring",
                joke_id=joke_id,
            )
            return

        try:
            scores = await score_joke(joke.response)
        except Exception as exc:
            duration_ms = int((time.perf_counter() - start) * 1000)
            await log.error(
                "worker_score_ai_failed",
                f"AI scoring failed for joke {joke_id}",
                joke_id=joke_id,
                duration_ms=duration_ms,
                exc=exc,
            )
            return

        if not scores:
            await log.warning(
                "worker_score_empty",
                f"AI returned empty scores for joke {joke_id}",
                joke_id=joke_id,
            )
            return

        joke.score_originality = scores.get("originality")
        joke.score_timing = scores.get("timing")
        joke.score_cleverness = scores.get("cleverness")
        await db.commit()

        duration_ms = int((time.perf_counter() - start) * 1000)
        await log.info(
            "worker_score_complete",
            f"Joke {joke_id} scored in {duration_ms}ms: {scores}",
            joke_id=joke_id,
            duration_ms=duration_ms,
            details={"scores": scores},
        )
