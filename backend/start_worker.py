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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
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
