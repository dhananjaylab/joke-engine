from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
import asyncio

from core.database import get_db
from models.joke import Joke
from schemas.joke import GenerateRequest, JokeResponse, PaginatedJokes
from services import ai
from dependencies.profile import get_profile
from models.profile import UserProfile

# ARQ imports
from arq import create_pool
from arq.connections import RedisSettings
from core.config import get_settings
from workers.fallback import score_joke_sync

router = APIRouter(prefix="/api/jokes", tags=["jokes"])
_settings = get_settings()


async def _enqueue_score(joke_id: int):
    """Enqueue background scoring task with fallback."""
    try:
        pool = await create_pool(RedisSettings.from_dsn(_settings.redis_url))
        await pool.enqueue_job("task_score_joke", joke_id)
        await pool.close(close_connection_pool=True)
        print(f"✓ Enqueued scoring task for joke {joke_id}")
    except Exception as e:
        # Fallback: score synchronously in background
        print(f"ARQ enqueue failed, using fallback scoring for joke {joke_id}: {e}")
        asyncio.create_task(score_joke_sync(joke_id))


@router.post("/generate", response_model=JokeResponse)
async def generate_joke(
    body: GenerateRequest,
    db: AsyncSession = Depends(get_db),
    profile: UserProfile = Depends(get_profile),
):
    composite_query = f"{body.query.strip()} [{body.style}]"

    # Cache lookup
    if not body.regenerate:
        result = await db.execute(
            select(Joke).where(func.lower(Joke.query) == composite_query.lower())
        )
        existing = result.scalar_one_or_none()
        if existing:
            return existing

    # Generate new joke
    joke_text = await ai.get_joke(body.query.strip(), body.style)

    new_joke = Joke(query=composite_query, response=joke_text)
    db.add(new_joke)
    await db.flush()   # get the ID before committing
    await db.refresh(new_joke)

    # Award XP (non-blocking)
    profile.xp += 5
    await db.commit()

    # Enqueue background scoring task
    asyncio.create_task(_enqueue_score(new_joke.id))

    return new_joke


@router.get("/stream")
async def stream_joke_sse(
    query: str = Query(..., max_length=100),
    style: str = Query("witty"),
    db: AsyncSession = Depends(get_db),
):
    """SSE endpoint — streams tokens then saves the completed joke."""

    async def event_generator():
        tokens: list[str] = []
        async for chunk in ai.stream_joke(query, style):
            tokens.append(chunk)
            yield chunk

        # Save completed joke after stream ends
        full_text = (
            "".join(tokens)
            .replace("data: ", "")
            .replace("\n\n", "")
            .replace("[DONE]", "")
            .strip()
        )
        if full_text:
            composite = f"{query.strip()} [{style}]"
            new_joke = Joke(query=composite, response=full_text)
            db.add(new_joke)
            await db.flush()
            await db.refresh(new_joke)
            await db.commit()
            
            # Enqueue background scoring task
            asyncio.create_task(_enqueue_score(new_joke.id))

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


@router.get("/history", response_model=PaginatedJokes)
async def get_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(8, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    offset = (page - 1) * page_size

    total_result = await db.execute(select(func.count(Joke.id)))
    total = total_result.scalar_one()

    jokes_result = await db.execute(
        select(Joke).order_by(Joke.created_at.desc()).offset(offset).limit(page_size)
    )
    jokes = jokes_result.scalars().all()

    return PaginatedJokes(
        jokes=jokes,
        total=total,
        page=page,
        pages=-(-total // page_size),  # ceiling division
    )


@router.get("/joke-of-the-day")
async def get_joke_of_the_day(db: AsyncSession = Depends(get_db)):
    """
    Get the joke of the day. Fetches from API Ninjas once per day (UTC timezone)
    and caches in database for all users.
    """
    from services.daily_joke import get_or_fetch_daily_joke
    
    try:
        joke_text = await get_or_fetch_daily_joke(db)
        return {"joke": joke_text}
    except Exception as e:
        print(f"Error fetching joke of the day: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"Failed to fetch joke of the day: {str(e)}"
        )


@router.delete("/{joke_id}", status_code=204)
async def delete_joke(joke_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Joke).where(Joke.id == joke_id))
    joke = result.scalar_one_or_none()
    if not joke:
        raise HTTPException(status_code=404, detail="Joke not found")
    await db.delete(joke)


@router.get("/{joke_id}", response_model=JokeResponse)
async def get_joke_by_id(joke_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Joke).where(Joke.id == joke_id))
    joke = result.scalar_one_or_none()
    if not joke:
        raise HTTPException(status_code=404, detail="Joke not found")
    return joke


@router.post("/{joke_id}/heckle")
async def heckle_joke(joke_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Joke).where(Joke.id == joke_id))
    joke = result.scalar_one_or_none()
    if not joke:
        raise HTTPException(status_code=404, detail="Joke not found")
    roast = await ai.heckle(joke.response)
    return {"roast": roast}


@router.post("/{joke_id}/explain")
async def explain_joke(joke_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Joke).where(Joke.id == joke_id))
    joke = result.scalar_one_or_none()
    if not joke:
        raise HTTPException(status_code=404, detail="Joke not found")
    explanation = await ai.explain(joke.response)
    return {"explanation": explanation}
