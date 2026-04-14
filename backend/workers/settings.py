from arq.connections import RedisSettings
from core.config import get_settings
from workers.tasks import task_score_joke

settings = get_settings()


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
