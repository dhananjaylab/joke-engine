from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()


@scheduler.scheduled_job('cron', day_of_week='mon', hour=0, minute=0)
async def weekly_challenge_reset():
    """Reset weekly challenge every Monday at midnight."""
    print("Weekly challenge reset triggered")
    # TODO: Implement challenge reset logic
