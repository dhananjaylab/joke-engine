from datetime import date, datetime, timezone
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.daily_joke import DailyJoke
from core.config import get_settings
from openai import AsyncOpenAI

settings = get_settings()
openai_client = AsyncOpenAI(api_key=settings.openai_api_key)


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
        print(f"✓ [CACHE HIT] Using cached joke for {today} (no API call)")
        return daily_joke.joke_text
    
    # Not in cache, fetch from API Ninjas
    print(f"⚡ [CACHE MISS] Fetching new joke from API Ninjas for {today}")
    raw_joke = await fetch_joke_from_api()
    
    # Enhance joke with emojis using LLM
    print(f"✨ [ENHANCING] Adding emojis to joke using LLM...")
    enhanced_joke = await enhance_joke_with_emojis(raw_joke)
    
    # Store in database
    new_daily_joke = DailyJoke(
        joke_date=today,
        joke_text=enhanced_joke,
        source="api_ninjas"
    )
    db.add(new_daily_joke)
    await db.commit()
    
    print(f"✓ [CACHED] Stored enhanced joke for {today} in database")
    return enhanced_joke


async def fetch_joke_from_api() -> str:
    """Fetch joke from API Ninjas."""
    if not settings.api_ninjas_key:
        raise ValueError("API Ninjas key not configured")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.api-ninjas.com/v1/jokeoftheday",
            headers={"X-Api-Key": settings.api_ninjas_key},
            timeout=10.0
        )
        response.raise_for_status()
        data = response.json()
        
        if data and len(data) > 0:
            return data[0].get("joke", "")
        else:
            raise ValueError("No joke returned from API")


async def enhance_joke_with_emojis(joke: str) -> str:
    """
    Use OpenAI to enhance the joke by adding relevant emojis.
    Makes the joke more visually appealing and engaging.
    """
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
        print(f"✨ Enhanced: {enhanced[:100]}...")
        return enhanced
        
    except Exception as e:
        print(f"⚠️ Failed to enhance joke with emojis: {e}")
        # Fallback: return original joke
        return joke


async def cleanup_old_jokes(db: AsyncSession, days_to_keep: int = 7):
    """
    Clean up old daily jokes to prevent database bloat.
    Keeps only the last N days of jokes.
    """
    from sqlalchemy import delete
    from datetime import timedelta
    
    cutoff_date = datetime.now(timezone.utc).date() - timedelta(days=days_to_keep)
    
    await db.execute(
        delete(DailyJoke).where(DailyJoke.joke_date < cutoff_date)
    )
    await db.commit()
    print(f"✓ Cleaned up jokes older than {cutoff_date}")
