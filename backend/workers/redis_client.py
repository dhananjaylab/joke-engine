"""
Singleton ARQ Redis pool.

FIX Phase-2: Previously every call to _enqueue_score() opened and immediately
closed a brand-new Redis connection pool (full TCP handshake per joke).
This module exposes a single shared pool that is created on first use and
closed during application shutdown.

Usage:
    from workers.redis_client import get_arq_pool, close_arq_pool

    pool = await get_arq_pool()
    await pool.enqueue_job("task_score_joke", joke_id)
"""
from __future__ import annotations

from arq import create_pool
from arq.connections import RedisSettings

from core.config import get_settings
from core.logging import get_logger

log = get_logger("workers.redis_client")

_pool = None


async def get_arq_pool():
    """Return the shared ARQ connection pool, creating it on first call."""
    global _pool
    if _pool is None:
        settings = get_settings()
        _pool = await create_pool(RedisSettings.from_dsn(settings.redis_url))
        await log.info(
            "arq_pool_created",
            "Singleton ARQ Redis pool created",
            details={"redis_url": settings.redis_url.split("@")[-1]},
        )
    return _pool


async def close_arq_pool() -> None:
    """Close the pool gracefully — call from lifespan shutdown."""
    global _pool
    if _pool is not None:
        await _pool.close(close_connection_pool=True)
        _pool = None
        await log.info("arq_pool_closed", "ARQ Redis pool closed")
