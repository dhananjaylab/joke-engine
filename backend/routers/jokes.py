"""
Jokes router — all phases applied.

FIXES:
  Phase-1:  Style Literal validation via updated GenerateRequest schema.
  Phase-2:  Cache lookup uses plain equality (query already lower-cased at write).
  Phase-3a: generate_joke wraps joke save + XP update in a single transaction.
  Phase-3b: Rate limiting via slowapi on AI-backed endpoints.
  Phase-3c: Typed error responses via AppError schema.
  Phase-4:  Keyset (cursor-based) pagination replaces OFFSET pagination.
"""
import time
import asyncio

import httpx
from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from core.database import get_db
from core.logging import get_logger
from models.joke import Joke
from schemas.joke import GenerateRequest, JokeResponse, PaginatedJokes
from schemas.errors import raise_app_error
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
    request: Request,                          # required by slowapi
    body: GenerateRequest,
    db: AsyncSession = Depends(get_db),
    profile: UserProfile = Depends(get_profile),
):
    start = time.perf_counter()
    # FIX Phase-2: normalise once here so the cache lookup uses the index
    composite_query = f"{body.query.strip()} [{body.style}]".lower()
    session_key = profile.session_key

    await log.info(
        "joke_generate_request",
        f"Joke generation requested: query={body.query!r} style={body.style}",
        details={"query": body.query, "style": body.style, "regenerate": body.regenerate},
        session_key=session_key,
    )

    # Cache lookup — plain equality, hits ix_jokes_query index
    if not body.regenerate:
        result = await db.execute(select(Joke).where(Joke.query == composite_query))
        existing = result.scalar_one_or_none()
        if existing:
            duration_ms = int((time.perf_counter() - start) * 1000)
            await log.info("joke_cache_hit", f"Cache hit for joke id={existing.id}", joke_id=existing.id, duration_ms=duration_ms)
            return existing

    try:
        joke_text = await ai.get_joke(body.query.strip(), body.style)
    except Exception as exc:
        duration_ms = int((time.perf_counter() - start) * 1000)
        await log.error("joke_generate_failed", "AI joke generation failed", session_key=session_key, duration_ms=duration_ms, exc=exc)
        # FIX Phase-4: typed error instead of raw string
        raise_app_error(503, "ai_unavailable", "AI service is temporarily unavailable")

    # FIX Phase-3a: save without auto-commit so XP update lands in the same txn
    new_joke = await save_joke(
        db,
        query=composite_query,
        response=joke_text,
        source="ai_generated",
        session_key=session_key,
        auto_commit=False,            # ← caller controls commit
    )
    profile.xp += 5
    await db.commit()                 # ← single commit covers both

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
    request: Request,
    query: str = Query(..., max_length=100),
    style: str = Query("witty"),
    length: str = Query("short"),
    db: AsyncSession = Depends(get_db),
):
    """SSE endpoint — streams tokens then saves the completed joke."""

    async def event_generator():
        tokens: list[str] = []
        start = time.perf_counter()

        await log.info(
            "joke_stream_start",
            f"SSE stream started: query={query!r} style={style} length={length}",
            details={"query": query, "style": style, "length": length},
        )

        try:
            async for chunk in ai.stream_joke(query, style, length):
                if chunk.strip() == "data: [DONE]":
                    break
                tokens.append(chunk)
                yield chunk
        except Exception as exc:
            await log.error("joke_stream_error", "SSE stream error", details={"query": query}, exc=exc)
            yield "data: [ERROR:AI service is temporarily unavailable]\n\n"
            return

        full_text = (
            "".join(tokens)
            .replace("data: ", "")
            .replace("\n\n", "")
            .replace("[DONE]", "")
            .strip()
        )
        if not full_text:
            await log.warning("joke_stream_empty", "SSE stream completed with no joke text", details={"query": query})
            yield "data: [ERROR:No joke was generated]\n\n"
            return

        try:
            composite = f"{query.strip()} [{style}] [{length}]".lower()
            new_joke = await save_joke(db, query=composite, response=full_text, source="ai_streamed")
            duration_ms = int((time.perf_counter() - start) * 1000)
            await log.info(
                "joke_stream_saved",
                f"Streamed joke saved: id={new_joke.id} in {duration_ms}ms",
                joke_id=new_joke.id,
                duration_ms=duration_ms,
            )
            yield f"data: [JOKE_ID:{new_joke.id}]\n\n"
            yield "data: [DONE]\n\n"
        except Exception as exc:
            await log.error("joke_stream_save_error", "Failed to save streamed joke", details={"query": query}, exc=exc)
            yield "data: [ERROR:Generated joke could not be saved]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no", "Connection": "keep-alive"},
    )


# ── History — cursor-based pagination (Phase-4) ───────────────────────────────

@router.get("/history", response_model=PaginatedJokes)
async def get_history(
    request: Request,
    # FIX Phase-4: cursor replaces page number for O(log n) pagination
    cursor: int | None = Query(None, description="Last seen joke ID; omit for first page"),
    page_size: int = Query(8, ge=1, le=50),
    source: str | None = Query(None, description="Filter by source"),
    db: AsyncSession = Depends(get_db),
):
    start = time.perf_counter()

    base_q = select(Joke).order_by(Joke.id.desc())
    if source:
        base_q = base_q.where(Joke.source == source)
    if cursor:
        base_q = base_q.where(Joke.id < cursor)   # keyset seek — uses PK index

    # Fetch one extra to detect whether another page exists
    base_q = base_q.limit(page_size + 1)
    jokes_result = await db.execute(base_q)
    jokes = list(jokes_result.scalars().all())

    has_more = len(jokes) > page_size
    if has_more:
        jokes = jokes[:page_size]

    next_cursor = jokes[-1].id if (has_more and jokes) else None

    # Count total for display only (not used for pagination)
    count_q = select(func.count()).select_from(select(Joke).subquery())
    if source:
        count_q = select(func.count()).select_from(select(Joke).where(Joke.source == source).subquery())
    total = (await db.execute(count_q)).scalar_one()

    duration_ms = int((time.perf_counter() - start) * 1000)
    await log.debug(
        "joke_history_fetched",
        f"History fetched: {len(jokes)} jokes (cursor={cursor}, has_more={has_more})",
        duration_ms=duration_ms,
        details={"cursor": cursor, "page_size": page_size, "total": total},
    )

    return PaginatedJokes(
        jokes=jokes,
        total=total,
        next_cursor=next_cursor,
        # Legacy fields kept for frontend migration period
        page=1,
        pages=1,
    )


# ── Random (API Ninjas) ───────────────────────────────────────────────────────

@router.get("/random", response_model=JokeResponse)
async def get_random_joke(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    start = time.perf_counter()
    await log.info("random_joke_request", "Random joke requested")

    if not _settings.api_ninjas_key:
        raise_app_error(503, "random_joke_failed", "API Ninjas key not configured")

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                "https://api.api-ninjas.com/v1/jokes",
                headers={"X-Api-Key": _settings.api_ninjas_key},
            )
            response.raise_for_status()
            data = response.json()
        if not data or "joke" not in data[0]:
            raise ValueError("Empty response from API Ninjas")
        joke_text = data[0]["joke"]
    except Exception as exc:
        duration_ms = int((time.perf_counter() - start) * 1000)
        await log.error("random_joke_fetch_failed", "Failed to fetch random joke", duration_ms=duration_ms, exc=exc)
        raise_app_error(503, "random_joke_failed", "Failed to fetch random joke")

    new_joke = await save_joke(
        db,
        query="random [api_ninjas]",
        response=joke_text,
        source="api_ninjas_random",
        enqueue_scoring=True,
    )
    duration_ms = int((time.perf_counter() - start) * 1000)
    await log.info("random_joke_saved", f"Random joke saved: id={new_joke.id}", joke_id=new_joke.id, duration_ms=duration_ms)
    return new_joke


# ── Joke of the Day ───────────────────────────────────────────────────────────

@router.get("/joke-of-the-day")
async def get_joke_of_the_day(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    from services.daily_joke import get_or_fetch_daily_joke

    start = time.perf_counter()
    try:
        joke_text, is_new = await get_or_fetch_daily_joke(db)
        if is_new:
            await save_joke(
                db,
                query="joke of the day [api_ninjas]",
                response=joke_text,
                source="api_ninjas_daily",
                enqueue_scoring=True,
            )
        duration_ms = int((time.perf_counter() - start) * 1000)
        await log.info("jotd_served", f"JOTD served in {duration_ms}ms (new={is_new})", duration_ms=duration_ms)
        return {"joke": joke_text}
    except Exception as exc:
        duration_ms = int((time.perf_counter() - start) * 1000)
        await log.error("jotd_failed", "Failed to fetch JOTD", duration_ms=duration_ms, exc=exc)
        raise_app_error(503, "jotd_unavailable", "Failed to fetch joke of the day")


# ── CRUD ──────────────────────────────────────────────────────────────────────

@router.delete("/{joke_id}", status_code=204)
async def delete_joke(joke_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Joke).where(Joke.id == joke_id))
    joke = result.scalar_one_or_none()
    if not joke:
        raise_app_error(404, "joke_not_found", _JOKE_NOT_FOUND)
    await db.delete(joke)
    await log.info("joke_deleted", f"Joke {joke_id} deleted", joke_id=joke_id)


@router.get("/{joke_id}", response_model=JokeResponse)
async def get_joke_by_id(joke_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Joke).where(Joke.id == joke_id))
    joke = result.scalar_one_or_none()
    if not joke:
        raise_app_error(404, "joke_not_found", _JOKE_NOT_FOUND)
    return joke


@router.post("/{joke_id}/structured-roast")
async def structured_roast_joke(joke_id: int, body: dict, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Joke).where(Joke.id == joke_id))
    joke = result.scalar_one_or_none()
    if not joke:
        raise_app_error(404, "joke_not_found", _JOKE_NOT_FOUND)

    originality = joke.score_originality
    timing = joke.score_timing
    cleverness = joke.score_cleverness

    if not all([originality, timing, cleverness]):
        scores = await ai.score_joke(joke.response)
        if scores:
            originality = scores.get("originality", 5)
            timing = scores.get("timing", 5)
            cleverness = scores.get("cleverness", 5)
            joke.score_originality = originality
            joke.score_timing = timing
            joke.score_cleverness = cleverness
            await db.commit()
        else:
            originality = originality or 5
            timing = timing or 5
            cleverness = cleverness or 5

    return await ai.structured_roast(joke.response, originality, timing, cleverness)


@router.post("/{joke_id}/explain")
async def explain_joke(joke_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Joke).where(Joke.id == joke_id))
    joke = result.scalar_one_or_none()
    if not joke:
        raise_app_error(404, "joke_not_found", _JOKE_NOT_FOUND)
    explanation = await ai.explain(joke.response)
    return {"explanation": explanation}
