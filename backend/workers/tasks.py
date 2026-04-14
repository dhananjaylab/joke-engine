"""ARQ task definitions. Run worker with: arq workers.settings.WorkerSettings"""
from core.database import AsyncSessionLocal
from models.joke import Joke
from services.ai import score_joke
from sqlalchemy import select


async def task_score_joke(ctx, joke_id: int):
    """Background task: score a joke on 3 dimensions."""
    scores = await score_joke(f"joke_{joke_id}")  # Placeholder - need actual joke text
    if not scores:
        return

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Joke).where(Joke.id == joke_id))
        joke = result.scalar_one_or_none()
        if joke:
            joke.score_originality = scores.get("originality")
            joke.score_timing = scores.get("timing")
            joke.score_cleverness = scores.get("cleverness")
            await db.commit()
