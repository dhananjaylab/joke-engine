#!/usr/bin/env python3
"""
Start ARQ worker for background tasks.
Usage: python start_worker.py

Note: If Redis connection is unstable, the app will fall back to synchronous scoring.
"""
import logging
import sys
from arq import run_worker
from workers.settings import WorkerSettings
from core.logging import setup_logging

# Configure logging
setup_logging(log_level="INFO")


if __name__ == "__main__":
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
