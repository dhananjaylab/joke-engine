import time
import asyncio

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from core.database import get_db
from core.logging import get_logger
from models.joke import Joke
from schemas.joke import GenerateRequest, JokeResponse, PaginatedJokes
from services import ai
from services.joke_store import save_joke
from dependencies.profile import get_profile
from models.profile import UserProfile
from core.config import get_settings

router = APIRouter(prefix="/api/jokes", tags=["jokes"])
_settings = get_settings()
log = get_logger("routers.jokes")

_JOKE_NOT_FOUND = "Joke not found"


# ── Generate (single-shot AI) ─────────────────────────────────────────────────

@router.post("/generate", response_model=JokeResponse)
async def generate_joke(
    body: GenerateRequest,
    db: AsyncSession = Depends(get_db),
    profile: UserProfile = Depends(get_profile),
):
    start = time.perf_counter()
    composite_query = f"{body.query.strip()} [{body.style}]"
    session_key = profile.session_key

    await log.info(
        "joke_generate_request",
        f"Joke generation requested: query={body.query!r} style={body.style} regenerate={body.regenerate}",
        details={"query": body.query, "style": body.style, "regenerate": body.regenerate},
        session_key=session_key,
    )

    # Cache lookup (skip on regenerate)
    if not body.regenerate:
        result = await db.execute(
            select(Joke).where(func.lower(Joke.query) == composite_query.lower())
        )
        existing = result.scalar_one_or_none()
        if existing:
            duration_ms = int((time.perf_counter() - start) * 1000)
            await log.info(
                "joke_cache_hit",
                f"Cache hit for joke id={existing.id}",
                joke_id=existing.id,
                session_key=session_key,
                duration_ms=duration_ms,
                details={"query": composite_query},
            )
            return existing

    # Generate via AI
    try:
        joke_text = await ai.get_joke(body.query.strip(), body.style)
    except Exception as exc:
        duration_ms = int((time.perf_counter() - start) * 1000)
        await log.error(
            "joke_generate_failed",
            "AI joke generation failed",
            details={"query": body.query, "style": body.style},
            session_key=session_key,
            duration_ms=duration_ms,
            exc=exc,
        )
        raise HTTPException(status_code=503, detail="AI service unavailable")

    # Persist via central store
    new_joke = await save_joke(
        db,
        query=composite_query,
        response=joke_text,
        source="ai_generated",
        session_key=session_key,
    )

    profile.xp += 5
    await db.commit()

    duration_ms = int((time.perf_counter() - start) * 1000)
    await log.info(
        "joke_generated",
        f"New joke saved: id={new_joke.id} in {duration_ms}ms",
        joke_id=new_joke.id,
        session_key=session_key,
        duration_ms=duration_ms,
        details={"query": composite_query, "xp_awarded": 5, "new_xp": profile.xp},
    )
    return new_joke


# ── Stream (SSE) ──────────────────────────────────────────────────────────────

@router.get("/stream")
async def stream_joke_sse(
    query: str = Query(..., max_length=100),
    style: str = Query("witty"),
    db: AsyncSession = Depends(get_db),
):
    """SSE endpoint — streams tokens then saves the completed joke."""

    async def event_generator():
        tokens: list[str] = []
        start = time.perf_counter()

        await log.info(
            "joke_stream_start",
            f"SSE stream started: query={query!r} style={style}",
            details={"query": query, "style": style},
        )

        try:
            async for chunk in ai.stream_joke(query, style):
                tokens.append(chunk)
                yield chunk
        except Exception as exc:
            await log.error(
                "joke_stream_error",
                "SSE stream encountered an error",
                details={"query": query, "style": style},
                exc=exc,
            )
            return

        full_text = (
            "".join(tokens)
            .replace("data: ", "")
            .replace("\n\n", "")
            .replace("[DONE]", "")
            .strip()
        )
        if full_text:
            composite = f"{query.strip()} [{style}]"
            new_joke = await save_joke(
                db,
                query=composite,
                response=full_text,
                source="ai_streamed",
            )
            duration_ms = int((time.perf_counter() - start) * 1000)
            await log.info(
                "joke_stream_saved",
                f"Streamed joke saved: id={new_joke.id} in {duration_ms}ms",
                joke_id=new_joke.id,
                duration_ms=duration_ms,
                details={"query": composite, "text_length": len(full_text)},
            )
            # Send the joke ID as the final event
            yield f"data: [JOKE_ID:{new_joke.id}]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


# ── History ───────────────────────────────────────────────────────────────────

@router.get("/history", response_model=PaginatedJokes)
async def get_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(8, ge=1, le=50),
    source: str = Query(None, description="Filter by source (e.g. api_ninjas_random)"),
    db: AsyncSession = Depends(get_db),
):
    start = time.perf_counter()
    offset = (page - 1) * page_size

    base_q = select(Joke)
    if source:
        base_q = base_q.where(Joke.source == source)

    total_result = await db.execute(select(func.count()).select_from(base_q.subquery()))
    total = total_result.scalar_one()

    jokes_result = await db.execute(
        base_q.order_by(Joke.created_at.desc()).offset(offset).limit(page_size)
    )
    jokes = jokes_result.scalars().all()

    duration_ms = int((time.perf_counter() - start) * 1000)
    await log.debug(
        "joke_history_fetched",
        f"History page {page} fetched: {len(jokes)}/{total} jokes",
        duration_ms=duration_ms,
        details={"page": page, "page_size": page_size, "total": total, "source_filter": source},
    )

    return PaginatedJokes(
        jokes=jokes,
        total=total,
        page=page,
        pages=-(-total // page_size),
    )


# ── Random (API Ninjas) ───────────────────────────────────────────────────────

@router.get("/random", response_model=JokeResponse)
async def get_random_joke(
    db: AsyncSession = Depends(get_db),
):
    """
    Fetch one random joke from API Ninjas /v1/jokes, persist it to Neon DB,
    and return the full JokeResponse (with id, source, scores, etc.).
    Free tier always returns 1 joke.
    """
    start = time.perf_counter()
    await log.info("random_joke_request", "Random joke requested")

    if not _settings.api_ninjas_key:
        await log.error("random_joke_no_key", "API Ninjas key not configured")
        raise HTTPException(status_code=503, detail="API Ninjas key not configured")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.api-ninjas.com/v1/jokes",
                headers={"X-Api-Key": _settings.api_ninjas_key},
                timeout=10.0,
            )
            response.raise_for_status()
            data = response.json()

        if not data or "joke" not in data[0]:
            raise ValueError("Empty response from API Ninjas")

        joke_text = data[0]["joke"]

    except Exception as exc:
        duration_ms = int((time.perf_counter() - start) * 1000)
        await log.error(
            "random_joke_fetch_failed",
            "Failed to fetch random joke from API Ninjas",
            duration_ms=duration_ms,
            exc=exc,
        )
        raise HTTPException(status_code=503, detail="Failed to fetch random joke")

    # Persist to Neon DB
    new_joke = await save_joke(
        db,
        query="random [api_ninjas]",
        response=joke_text,
        source="api_ninjas_random",
        session_key=None,
        enqueue_scoring=True,
    )

    duration_ms = int((time.perf_counter() - start) * 1000)
    await log.info(
        "random_joke_saved",
        f"Random joke fetched and saved: id={new_joke.id} in {duration_ms}ms",
        joke_id=new_joke.id,
        duration_ms=duration_ms,
        details={"preview": joke_text[:80]},
    )
    return new_joke


# ── Joke of the Day ───────────────────────────────────────────────────────────

@router.get("/joke-of-the-day")
async def get_joke_of_the_day(db: AsyncSession = Depends(get_db)):
    """
    Get the joke of the day. Fetches from API Ninjas once per day (UTC),
    caches in daily_jokes table, and also mirrors into the jokes table
    so it appears in history and gets AI-scored.
    """
    from services.daily_joke import get_or_fetch_daily_joke

    start = time.perf_counter()
    await log.info("jotd_request", "Joke-of-the-day requested")

    try:
        joke_text, is_new = await get_or_fetch_daily_joke(db)
        duration_ms = int((time.perf_counter() - start) * 1000)

        # Mirror into jokes table only when freshly fetched (not on cache hits)
        if is_new:
            await save_joke(
                db,
                query="joke of the day [api_ninjas]",
                response=joke_text,
                source="api_ninjas_daily",
                session_key=None,
                enqueue_scoring=True,
            )
            await log.info(
                "jotd_mirrored",
                "Joke-of-the-day mirrored into jokes table",
                duration_ms=duration_ms,
            )

        await log.info(
            "jotd_served",
            f"Joke-of-the-day served in {duration_ms}ms (new={is_new})",
            duration_ms=duration_ms,
        )
        return {"joke": joke_text}

    except Exception as exc:
        duration_ms = int((time.perf_counter() - start) * 1000)
        await log.error(
            "jotd_failed",
            "Failed to fetch joke of the day",
            duration_ms=duration_ms,
            exc=exc,
        )
        raise HTTPException(
            status_code=503,
            detail=f"Failed to fetch joke of the day: {str(exc)}"
        )


# ── CRUD ──────────────────────────────────────────────────────────────────────

@router.delete("/{joke_id}", status_code=204)
async def delete_joke(joke_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Joke).where(Joke.id == joke_id))
    joke = result.scalar_one_or_none()
    if not joke:
        await log.warning("joke_delete_not_found", f"Delete requested for non-existent joke {joke_id}", joke_id=joke_id)
        raise HTTPException(status_code=404, detail=_JOKE_NOT_FOUND)
    await db.delete(joke)
    await log.info("joke_deleted", f"Joke {joke_id} deleted", joke_id=joke_id)


@router.get("/{joke_id}", response_model=JokeResponse)
async def get_joke_by_id(joke_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Joke).where(Joke.id == joke_id))
    joke = result.scalar_one_or_none()
    if not joke:
        await log.warning("joke_not_found", f"Joke {joke_id} not found", joke_id=joke_id)
        raise HTTPException(status_code=404, detail=_JOKE_NOT_FOUND)
    await log.debug("joke_fetched", f"Joke {joke_id} fetched", joke_id=joke_id)
    return joke


@router.post("/{joke_id}/heckle")
async def heckle_joke(joke_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Joke).where(Joke.id == joke_id))
    joke = result.scalar_one_or_none()
    if not joke:
        await log.warning("heckle_joke_not_found", f"Heckle requested for non-existent joke {joke_id}", joke_id=joke_id)
        raise HTTPException(status_code=404, detail=_JOKE_NOT_FOUND)
    await log.info("heckle_request", f"Heckle requested for joke {joke_id}", joke_id=joke_id)
    roast = await ai.heckle(joke.response)
    return {"roast": roast}


@router.post("/{joke_id}/explain")
async def explain_joke(joke_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Joke).where(Joke.id == joke_id))
    joke = result.scalar_one_or_none()
    if not joke:
        await log.warning("explain_joke_not_found", f"Explain requested for non-existent joke {joke_id}", joke_id=joke_id)
        raise HTTPException(status_code=404, detail=_JOKE_NOT_FOUND)
    await log.info("explain_request", f"Explain requested for joke {joke_id}", joke_id=joke_id)
    explanation = await ai.explain(joke.response)
    return {"explanation": explanation}
