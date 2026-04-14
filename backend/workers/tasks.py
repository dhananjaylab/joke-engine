"""ARQ task definitions. Run worker with: arq workers.settings.WorkerSettings"""
from core.database import AsyncSessionLocal
from models.joke import Joke
from services.ai import score_joke
from sqlalchemy import select


async def task_score_joke(ctx, joke_id: int):
    """Background task: score a joke on 3 dimensions."""
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Joke).where(Joke.id == joke_id))
        joke = result.scalar_one_or_none()
        if not joke:
            return

        # Score the joke text
        scores = await score_joke(joke.response)
        if not scores:
            return

        # Update the joke with scores
        joke.score_originality = scores.get("originality")
        joke.score_timing = scores.get("timing")
        joke.score_cleverness = scores.get("cleverness")
        await db.commit()
