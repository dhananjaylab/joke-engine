from arq.connections import RedisSettings
from core.config import get_settings
from core.logging import get_logger, start_db_log_flush
from workers.tasks import task_score_joke

settings = get_settings()
log = get_logger("workers.settings")


async def startup(ctx):
    """Startup hook called by ARQ worker on start."""
    start_db_log_flush()
    await log.info(
        "worker_startup",
        "ARQ worker starting",
        details={
            "tasks": [f.__name__ for f in WorkerSettings.functions],
            "redis_host": WorkerSettings.redis_settings.host,
            "redis_port": WorkerSettings.redis_settings.port,
            "max_jobs": WorkerSettings.max_jobs,
            "job_timeout": WorkerSettings.job_timeout,
        },
    )


async def shutdown(ctx):
    """Shutdown hook called by ARQ worker on stop."""
    await log.info("worker_shutdown", "ARQ worker shutting down")


class WorkerSettings:
    """ARQ Worker configuration"""
    functions = [task_score_joke]
    redis_settings = RedisSettings.from_dsn(settings.redis_url)
    max_jobs = 10
    job_timeout = 30
    keep_result = 3600  # Keep results for 1 hour
    max_tries = 3
    poll_delay = 0.5  # Poll every 0.5 seconds
    queue_read_limit = 10
    on_startup = startup
    on_shutdown = shutdown
