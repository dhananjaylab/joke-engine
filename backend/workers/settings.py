from arq.connections import RedisSettings
from core.config import get_settings
from workers.tasks import task_score_joke

settings = get_settings()


class WorkerSettings:
    functions = [task_score_joke]
    redis_settings = RedisSettings.from_dsn(
        settings.redis_url,
        retry_on_timeout=True,
        socket_keepalive=True,
        socket_keepalive_options={},
        health_check_interval=30,
    )
    max_jobs = 10
    job_timeout = 30
    keep_result = 3600  # Keep results for 1 hour
    max_tries = 3
