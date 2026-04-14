"""
Fallback scoring mechanism when ARQ worker is not available.
This allows the app to work without Redis/ARQ in development.
"""
import asyncio
from core.database import AsyncSessionLocal
from models.joke import Joke
from services.ai import score_joke
from sqlalchemy import select


async def score_joke_sync(joke_id: int):
    """Score a joke synchronously (fallback when worker is unavailable)"""
    try:
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(Joke).where(Joke.id == joke_id))
            joke = result.scalar_one_or_none()
            if not joke:
                return

            scores = await score_joke(joke.response)
            if not scores:
                return

            joke.score_originality = scores.get("originality")
            joke.score_timing = scores.get("timing")
            joke.score_cleverness = scores.get("cleverness")
            await db.commit()
            print(f"✓ Scored joke {joke_id} synchronously: {scores}")
    except Exception as e:
        print(f"Fallback scoring failed for joke {joke_id}: {e}")
