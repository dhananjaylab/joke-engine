"""Clear daily jokes cache to test LLM enhancement."""
import asyncio
from core.database import AsyncSessionLocal
from models.daily_joke import DailyJoke
from sqlalchemy import delete


async def clear_cache():
    async with AsyncSessionLocal() as db:
        await db.execute(delete(DailyJoke))
        await db.commit()
        print("✓ Cleared daily jokes cache - next request will fetch and enhance a new joke")


if __name__ == "__main__":
    asyncio.run(clear_cache())
