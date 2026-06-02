"""
Lightweight Redis TTL cache.

FIX Phase-4: Redis is already deployed for ARQ. This module reuses that
connection to cache hot read paths (JOTD, history page 1) without adding
any new infrastructure.

Usage:
    from services.cache import cache_get, cache_set, cache_delete

    # Store with a 60-second TTL
    await cache_set("jotd:2026-05-30", {"joke": "..."}, ttl=86400)

    # Retrieve (returns None on miss)
    data = await cache_get("jotd:2026-05-30")
"""
from __future__ import annotations

import json
from typing import Any

import redis.asyncio as aioredis

from core.config import get_settings
from core.logging import get_logger

log = get_logger("services.cache")

_redis: aioredis.Redis | None = None


async def _get_redis() -> aioredis.Redis:
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(
            get_settings().redis_url,
            encoding="utf-8",
            decode_responses=True,
        )
    return _redis


async def close_cache() -> None:
    """Close the Redis connection — call from lifespan shutdown."""
    global _redis
    if _redis is not None:
        await _redis.aclose()
        _redis = None


async def cache_get(key: str) -> Any | None:
    """Return the cached value or None on miss / error."""
    try:
        r = await _get_redis()
        raw = await r.get(key)
        if raw is None:
            return None
        return json.loads(raw)
    except Exception as exc:
        await log.warning("cache_get_error", f"Cache GET failed for key={key!r}", exc=exc)
        return None


async def cache_set(key: str, value: Any, ttl: int = 60) -> None:
    """Store *value* as JSON with a TTL in seconds. Silently no-ops on error."""
    try:
        r = await _get_redis()
        await r.setex(key, ttl, json.dumps(value))
    except Exception as exc:
        await log.warning("cache_set_error", f"Cache SET failed for key={key!r}", exc=exc)


async def cache_delete(key: str) -> None:
    """Delete a key. Silently no-ops on error."""
    try:
        r = await _get_redis()
        await r.delete(key)
    except Exception as exc:
        await log.warning("cache_delete_error", f"Cache DELETE failed for key={key!r}", exc=exc)
