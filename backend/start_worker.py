#!/usr/bin/env python3
"""
Start ARQ worker for background tasks.
Usage: python start_worker.py

Note: If Redis connection is unstable, the app will fall back to synchronous scoring.
"""
import asyncio
import logging
import sys
from arq import run_worker
from workers.settings import WorkerSettings
from core.logging import setup_logging, start_db_log_flush, get_logger

# Configure logging
setup_logging(log_level="INFO")
log = get_logger("start_worker")


async def _startup():
    """Start the DB log flush loop before the worker begins."""
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


if __name__ == "__main__":
    asyncio.run(_startup())

    logger = logging.getLogger("start_worker")
    logger.info("Starting ARQ worker...")
    logger.info(f"Available tasks: {[f.__name__ for f in WorkerSettings.functions]}")
    logger.info(f"Redis: {WorkerSettings.redis_settings.host}:{WorkerSettings.redis_settings.port}")
    logger.info("Note: Worker will poll Redis every 0.5 seconds for new jobs")
    logger.info("Press Ctrl+C to stop")

    try:
        run_worker(WorkerSettings)
    except KeyboardInterrupt:
        logger.info("\nWorker stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Worker failed: {e}")
        logger.error("If Redis connection is unstable, the app will use fallback scoring")
        sys.exit(1)
