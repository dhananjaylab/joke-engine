from apscheduler.schedulers.asyncio import AsyncIOScheduler
from core.database import AsyncSessionLocal

scheduler = AsyncIOScheduler()


@scheduler.scheduled_job('cron', day_of_week='mon', hour=0, minute=0)
async def weekly_challenge_reset():
    """Reset weekly challenge every Monday at midnight."""
    print("Weekly challenge reset triggered")
    # TODO: Implement challenge reset logic


@scheduler.scheduled_job('cron', hour=1, minute=0)
async def cleanup_old_daily_jokes():
    """Clean up old daily jokes every day at 1 AM UTC."""
    from services.daily_joke import cleanup_old_jokes
    
    async with AsyncSessionLocal() as db:
        try:
            await cleanup_old_jokes(db, days_to_keep=7)
        except Exception as e:
            print(f"Error cleaning up old jokes: {e}")
