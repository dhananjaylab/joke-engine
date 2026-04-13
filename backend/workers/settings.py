from core.config import get_settings

settings = get_settings()


class WorkerSettings:
    functions = ["workers.tasks.task_score_joke"]
    redis_settings = settings.redis_url
    max_jobs = 10
    job_timeout = 30
