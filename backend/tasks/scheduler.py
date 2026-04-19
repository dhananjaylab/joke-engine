from apscheduler.schedulers.asyncio import AsyncIOScheduler
from core.database import AsyncSessionLocal
from core.logging import get_logger

scheduler = AsyncIOScheduler()
log = get_logger("tasks.scheduler")


@scheduler.scheduled_job('cron', day_of_week='mon', hour=0, minute=0)
async def weekly_challenge_reset():
    """Reset weekly challenge every Monday at midnight."""
    await log.info("scheduler_weekly_reset_start", "Weekly challenge reset triggered")
    try:
        # TODO: Implement challenge reset logic
        await log.info("scheduler_weekly_reset_complete", "Weekly challenge reset complete (stub)")
    except Exception as exc:
        await log.error("scheduler_weekly_reset_failed", "Weekly challenge reset failed", exc=exc)


@scheduler.scheduled_job('cron', hour=1, minute=0)
async def cleanup_old_daily_jokes():
    """Clean up old daily jokes every day at 1 AM UTC."""
    await log.info("scheduler_cleanup_start", "Daily joke cleanup job triggered")
    try:
        from services.daily_joke import cleanup_old_jokes
        async with AsyncSessionLocal() as db:
            await cleanup_old_jokes(db, days_to_keep=7)
        await log.info("scheduler_cleanup_complete", "Daily joke cleanup job finished")
    except Exception as exc:
        await log.error("scheduler_cleanup_failed", "Daily joke cleanup job failed", exc=exc)
