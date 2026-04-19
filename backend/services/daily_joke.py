import time
from datetime import date, datetime, timezone, timedelta

import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from openai import AsyncOpenAI

from models.daily_joke import DailyJoke
from core.config import get_settings
from core.logging import get_logger

settings = get_settings()
openai_client = AsyncOpenAI(api_key=settings.openai_api_key)
log = get_logger("services.daily_joke")


async def get_or_fetch_daily_joke(db: AsyncSession) -> str:
    """
    Get today's joke from database, or fetch from API Ninjas if not cached.
    Uses UTC timezone to determine the current date.
    """
    today = datetime.now(timezone.utc).date()

    # Try to get from database first
    result = await db.execute(
        select(DailyJoke).where(DailyJoke.joke_date == today)
    )
    daily_joke = result.scalar_one_or_none()

    if daily_joke:
        await log.info(
            "jotd_cache_hit",
            f"Daily joke cache hit for {today}",
            details={"date": str(today), "source": daily_joke.source},
        )
        return daily_joke.joke_text

    # Not in cache — fetch from API Ninjas
    await log.info("jotd_cache_miss", f"Daily joke cache miss for {today} — fetching from API Ninjas", details={"date": str(today)})
    start = time.perf_counter()

    try:
        raw_joke = await fetch_joke_from_api()
    except Exception as exc:
        await log.error("jotd_api_fetch_failed", "API Ninjas fetch failed", exc=exc)
        raise

    # Enhance joke with emojis using LLM
    await log.info("jotd_enhancing", "Enhancing daily joke with emojis via LLM")
    try:
        enhanced_joke = await enhance_joke_with_emojis(raw_joke)
    except Exception as exc:
        await log.warning("jotd_enhance_failed", "Emoji enhancement failed — using raw joke", exc=exc)
        enhanced_joke = raw_joke

    # Store in database
    new_daily_joke = DailyJoke(
        joke_date=today,
        joke_text=enhanced_joke,
        source="api_ninjas"
    )
    db.add(new_daily_joke)
    await db.commit()

    duration_ms = int((time.perf_counter() - start) * 1000)
    await log.info(
        "jotd_cached",
        f"Daily joke fetched, enhanced, and cached for {today} in {duration_ms}ms",
        duration_ms=duration_ms,
        details={"date": str(today), "preview": enhanced_joke[:80]},
    )
    return enhanced_joke


async def fetch_joke_from_api() -> str:
    """Fetch joke from API Ninjas."""
    if not settings.api_ninjas_key:
        raise ValueError("API Ninjas key not configured")

    start = time.perf_counter()
    await log.info("jotd_api_request", "Sending request to API Ninjas")

    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.api-ninjas.com/v1/jokeoftheday",
            headers={"X-Api-Key": settings.api_ninjas_key},
            timeout=10.0
        )
        response.raise_for_status()
        data = response.json()

        duration_ms = int((time.perf_counter() - start) * 1000)

        if data and len(data) > 0:
            joke_text = data[0].get("joke", "")
            await log.info(
                "jotd_api_success",
                f"API Ninjas returned joke in {duration_ms}ms",
                duration_ms=duration_ms,
                details={"preview": joke_text[:80], "status_code": response.status_code},
            )
            return joke_text
        else:
            await log.error(
                "jotd_api_empty",
                "API Ninjas returned empty response",
                details={"status_code": response.status_code, "body": str(data)},
            )
            raise ValueError("No joke returned from API")


async def enhance_joke_with_emojis(joke: str) -> str:
    """
    Use OpenAI to enhance the joke by adding relevant emojis.
    """
    start = time.perf_counter()
    await log.debug("jotd_enhance_start", "Starting emoji enhancement", details={"preview": joke[:80]})

    try:
        response = await openai_client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.7,
            max_tokens=300,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a comedy enhancement specialist. "
                        "Add relevant emojis to jokes to make them more visually appealing and fun. "
                        "Rules:\n"
                        "1. Add 2-4 emojis total (not too many)\n"
                        "2. Place emojis naturally within or at the end of the joke\n"
                        "3. Choose emojis that match the joke's theme\n"
                        "4. Keep the original joke text intact\n"
                        "5. Make it feel natural and not forced\n"
                        "Return ONLY the enhanced joke, nothing else."
                    )
                },
                {
                    "role": "user",
                    "content": f"Enhance this joke with emojis:\n\n{joke}"
                }
            ]
        )

        enhanced = response.choices[0].message.content.strip()
        duration_ms = int((time.perf_counter() - start) * 1000)
        await log.info(
            "jotd_enhance_complete",
            f"Emoji enhancement complete in {duration_ms}ms",
            duration_ms=duration_ms,
            details={"preview": enhanced[:80]},
        )
        return enhanced

    except Exception as exc:
        duration_ms = int((time.perf_counter() - start) * 1000)
        await log.warning(
            "jotd_enhance_failed",
            "Failed to enhance joke with emojis — returning original",
            duration_ms=duration_ms,
            exc=exc,
        )
        return joke


async def cleanup_old_jokes(db: AsyncSession, days_to_keep: int = 7):
    """
    Clean up old daily jokes to prevent database bloat.
    Keeps only the last N days of jokes.
    """
    cutoff_date = datetime.now(timezone.utc).date() - timedelta(days=days_to_keep)

    await log.info(
        "jotd_cleanup_start",
        f"Cleaning up daily jokes older than {cutoff_date}",
        details={"cutoff_date": str(cutoff_date), "days_to_keep": days_to_keep},
    )

    try:
        result = await db.execute(
            delete(DailyJoke).where(DailyJoke.joke_date < cutoff_date)
        )
        await db.commit()
        await log.info(
            "jotd_cleanup_complete",
            f"Daily joke cleanup complete — cutoff={cutoff_date}",
            details={"cutoff_date": str(cutoff_date)},
        )
    except Exception as exc:
        await log.error("jotd_cleanup_failed", "Daily joke cleanup failed", exc=exc)
        raise
