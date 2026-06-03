"""
Daily joke service — race condition and caching fixes applied.

FIXES:
  Phase-3a: Replaced SELECT-then-INSERT with a single atomic
            INSERT … ON CONFLICT DO NOTHING, eliminating the race
            condition where two simultaneous first-requests of the day
            both passed the SELECT check and then fought to INSERT.
  Phase-4:  Added Redis TTL cache (86400s) so repeat requests within
            the same day never touch the DB or the external API.
"""
from __future__ import annotations

import time
from datetime import date, datetime, timezone, timedelta

import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from models.daily_joke import DailyJoke
from core.config import get_settings
from core.logging import get_logger
from services.cache import cache_get, cache_set
from services import ai as ai_service

settings = get_settings()
log = get_logger("services.daily_joke")


def _cache_key(d: date) -> str:
    return f"jotd:{d.isoformat()}"


async def get_or_fetch_daily_joke(db: AsyncSession) -> tuple[str, bool]:
    """
    Return today's joke (UTC) and a bool indicating whether it was freshly fetched.

    Resolution order:
      1. Redis TTL cache  — fastest, no DB hit
      2. PostgreSQL row   — fast, single SELECT
      3. API Ninjas fetch — slow, then stored atomically via upsert
    """
    today = datetime.now(timezone.utc).date()

    # ── 1. Redis cache ──────────────────────────────────────────────────────
    cached = await cache_get(_cache_key(today))
    if cached:
        await log.info("jotd_redis_hit", f"JOTD served from Redis cache for {today}")
        return cached["joke"], False

    # ── 2. PostgreSQL row ───────────────────────────────────────────────────
    result = await db.execute(select(DailyJoke).where(DailyJoke.joke_date == today))
    row = result.scalar_one_or_none()
    if row:
        await log.info("jotd_db_hit", f"JOTD served from DB for {today}")
        await cache_set(_cache_key(today), {"joke": row.joke_text}, ttl=86400)
        return row.joke_text, False

    # ── 3. Fetch from API Ninjas, then upsert atomically ───────────────────
    await log.info("jotd_cache_miss", f"JOTD cache miss for {today} — fetching from API Ninjas")
    start = time.perf_counter()

    try:
        raw_joke = await fetch_joke_from_api()
    except Exception as exc:
        await log.error("jotd_api_fetch_failed", "API Ninjas fetch failed", exc=exc)
        raise

    try:
        enhanced_joke = await enhance_joke_with_emojis(raw_joke)
    except Exception as exc:
        await log.warning("jotd_enhance_failed", "Emoji enhancement failed — using raw joke", exc=exc)
        enhanced_joke = raw_joke

    # FIX Phase-3a: atomic upsert — if a concurrent request already inserted
    # today's row the conflict is silently ignored and we read the winner back.
    try:
        from sqlalchemy.dialects.postgresql import insert as pg_insert

        stmt = (
            pg_insert(DailyJoke)
            .values(joke_date=today, joke_text=enhanced_joke, source="api_ninjas")
            .on_conflict_do_nothing(index_elements=["joke_date"])
        )
        await db.execute(stmt)
        await db.commit()
    except Exception:
        # SQLite fallback (dev environment uses SQLite which has no ON CONFLICT syntax)
        await db.rollback()
        existing = (await db.execute(select(DailyJoke).where(DailyJoke.joke_date == today))).scalar_one_or_none()
        if not existing:
            db.add(DailyJoke(joke_date=today, joke_text=enhanced_joke, source="api_ninjas"))
            await db.commit()

    # Read back the winning row (ours or a concurrent winner)
    result = await db.execute(select(DailyJoke).where(DailyJoke.joke_date == today))
    winner = result.scalar_one()
    final_joke = winner.joke_text

    duration_ms = int((time.perf_counter() - start) * 1000)
    await log.info(
        "jotd_cached",
        f"JOTD fetched, enhanced, and stored for {today} in {duration_ms}ms",
        duration_ms=duration_ms,
        details={"date": str(today), "preview": final_joke[:80]},
    )

    await cache_set(_cache_key(today), {"joke": final_joke}, ttl=86400)
    return final_joke, True


async def fetch_joke_from_api() -> str:
    """Fetch a joke from API Ninjas /v1/jokeoftheday."""
    if not settings.api_ninjas_key:
        raise ValueError("API Ninjas key not configured")

    start = time.perf_counter()
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(
            "https://api.api-ninjas.com/v1/jokeoftheday",
            headers={"X-Api-Key": settings.api_ninjas_key},
        )
        response.raise_for_status()
        data = response.json()

    duration_ms = int((time.perf_counter() - start) * 1000)
    if not data or "joke" not in data[0]:
        raise ValueError("Empty response from API Ninjas")

    joke_text = data[0]["joke"]
    await log.info(
        "jotd_api_success",
        f"API Ninjas returned joke in {duration_ms}ms",
        duration_ms=duration_ms,
        details={"preview": joke_text[:80]},
    )
    return joke_text


async def enhance_joke_with_emojis(joke: str) -> str:
    """Use OpenAI to add 2–4 relevant emojis to the joke."""
    from openai import AsyncOpenAI

    client = AsyncOpenAI(
        api_key=settings.openai_api_key,
        max_retries=3,
        timeout=20.0,
    )
    start = time.perf_counter()
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.7,
            max_tokens=300,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a comedy enhancement specialist. Add 2–4 relevant emojis "
                        "to jokes naturally. Keep the original text intact. "
                        "Return ONLY the enhanced joke, nothing else."
                    ),
                },
                {"role": "user", "content": f"Enhance this joke with emojis:\n\n{joke}"},
            ],
        )
        enhanced = response.choices[0].message.content.strip()
        duration_ms = int((time.perf_counter() - start) * 1000)
        await log.info("jotd_enhance_complete", f"Emoji enhancement done in {duration_ms}ms", duration_ms=duration_ms)
        return enhanced
    except Exception as exc:
        duration_ms = int((time.perf_counter() - start) * 1000)
        await log.warning("jotd_enhance_failed", "Emoji enhancement failed", duration_ms=duration_ms, exc=exc)
        return joke


async def cleanup_old_jokes(db: AsyncSession, days_to_keep: int = 7) -> None:
    """Remove daily jokes older than *days_to_keep* days."""
    cutoff_date = datetime.now(timezone.utc).date() - timedelta(days=days_to_keep)
    await log.info("jotd_cleanup_start", f"Cleaning jokes older than {cutoff_date}")
    try:
        await db.execute(delete(DailyJoke).where(DailyJoke.joke_date < cutoff_date))
        await db.commit()
        await log.info("jotd_cleanup_complete", f"Cleanup done — cutoff={cutoff_date}")
    except Exception as exc:
        await log.error("jotd_cleanup_failed", "Cleanup failed", exc=exc)
        raise
