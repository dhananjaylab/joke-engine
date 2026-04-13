from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

# Weekly challenge or cleanup tasks can be added here
@scheduler.scheduled_job('interval', minutes=60)
async def example_task():
    print("Running background task...")
