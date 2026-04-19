import time
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.database import get_db
from core.config import get_settings
from core.logging import get_logger
from models.joke import Joke
from services.ai import generate_audio
from services.image import render_joke_card
from services.storage import storage

router = APIRouter(prefix="/api/share", tags=["share"])
settings = get_settings()
log = get_logger("routers.share")


@router.get("/{joke_id}/card.png")
async def joke_card_png(joke_id: int, db: AsyncSession = Depends(get_db)):
    start = time.perf_counter()
    result = await db.execute(select(Joke).where(Joke.id == joke_id))
    joke = result.scalar_one_or_none()
    if not joke:
        await log.warning("share_card_not_found", f"Card requested for non-existent joke {joke_id}", joke_id=joke_id)
        raise HTTPException(404)

    try:
        png_bytes = render_joke_card(joke.response, joke.query)
        duration_ms = int((time.perf_counter() - start) * 1000)
        await log.info(
            "share_card_generated",
            f"PNG card generated for joke {joke_id} ({len(png_bytes)} bytes) in {duration_ms}ms",
            joke_id=joke_id,
            duration_ms=duration_ms,
            details={"bytes": len(png_bytes)},
        )
        return StreamingResponse(
            iter([png_bytes]),
            media_type="image/png",
            headers={
                "Content-Disposition": f'attachment; filename="giggle-{joke_id}.png"',
                "Cache-Control": "public, max-age=86400",
            },
        )
    except Exception as exc:
        duration_ms = int((time.perf_counter() - start) * 1000)
        await log.error(
            "share_card_failed",
            f"PNG card generation failed for joke {joke_id}",
            joke_id=joke_id,
            duration_ms=duration_ms,
            exc=exc,
        )
        raise HTTPException(500, "Failed to generate card")


@router.get("/{joke_id}/audio")
async def joke_audio(joke_id: int, db: AsyncSession = Depends(get_db)):
    start = time.perf_counter()
    result = await db.execute(select(Joke).where(Joke.id == joke_id))
    joke = result.scalar_one_or_none()
    if not joke:
        await log.warning("share_audio_not_found", f"Audio requested for non-existent joke {joke_id}", joke_id=joke_id)
        raise HTTPException(404)

    # Generate and save audio if not exists
    if not joke.audio_url:
        await log.info("share_audio_generate", f"Generating TTS audio for joke {joke_id}", joke_id=joke_id)
        try:
            audio_bytes = await generate_audio(joke.response)
            joke.audio_url = await storage.save_audio(joke_id, audio_bytes)
            await db.commit()
            duration_ms = int((time.perf_counter() - start) * 1000)
            await log.info(
                "share_audio_saved",
                f"Audio saved for joke {joke_id} at {joke.audio_url} in {duration_ms}ms",
                joke_id=joke_id,
                duration_ms=duration_ms,
                details={"audio_url": joke.audio_url, "bytes": len(audio_bytes)},
            )
        except Exception as exc:
            duration_ms = int((time.perf_counter() - start) * 1000)
            await log.error(
                "share_audio_failed",
                f"Audio generation/save failed for joke {joke_id}",
                joke_id=joke_id,
                duration_ms=duration_ms,
                exc=exc,
            )
            raise HTTPException(500, "Failed to generate audio")
    else:
        await log.debug(
            "share_audio_cached",
            f"Serving cached audio for joke {joke_id}",
            joke_id=joke_id,
            details={"audio_url": joke.audio_url},
        )

    # For cloud storage, redirect to public URL
    if settings.use_cloud_storage:
        return Response(
            status_code=302,
            headers={"Location": joke.audio_url, "Cache-Control": "public, max-age=604800"}
        )

    # For local storage, serve the file
    audio_bytes = await storage.get_audio(joke.audio_url)
    if not audio_bytes:
        await log.error("share_audio_file_missing", f"Audio file missing on disk for joke {joke_id}", joke_id=joke_id)
        raise HTTPException(404, "Audio file not found")

    return Response(
        content=audio_bytes,
        media_type="audio/mpeg",
        headers={"Cache-Control": "public, max-age=604800"},
    )


@router.post("/{joke_id}/increment")
async def increment_share(joke_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Joke).where(Joke.id == joke_id))
    joke = result.scalar_one_or_none()
    if joke:
        joke.share_count += 1
        await db.commit()
        await log.info(
            "share_count_incremented",
            f"Share count for joke {joke_id} incremented to {joke.share_count}",
            joke_id=joke_id,
            details={"share_count": joke.share_count},
        )
    else:
        await log.warning("share_increment_not_found", f"Share increment for non-existent joke {joke_id}", joke_id=joke_id)
    return {"ok": True}
