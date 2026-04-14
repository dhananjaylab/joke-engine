import os
import hashlib
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.database import get_db
from core.config import get_settings
from models.joke import Joke
from services.ai import generate_audio
from services.image import render_joke_card
from services.storage import storage

router = APIRouter(prefix="/api/share", tags=["share"])
settings = get_settings()


@router.get("/{joke_id}/card.png")
async def joke_card_png(joke_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Joke).where(Joke.id == joke_id))
    joke = result.scalar_one_or_none()
    if not joke:
        raise HTTPException(404)

    png_bytes = render_joke_card(joke.response, joke.query)
    return StreamingResponse(
        iter([png_bytes]),
        media_type="image/png",
        headers={
            "Content-Disposition": f'attachment; filename="giggle-{joke_id}.png"',
            "Cache-Control": "public, max-age=86400",
        },
    )


@router.get("/{joke_id}/audio")
async def joke_audio(joke_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Joke).where(Joke.id == joke_id))
    joke = result.scalar_one_or_none()
    if not joke:
        raise HTTPException(404)

    # Generate and save audio if not exists
    if not joke.audio_url:
        audio_bytes = await generate_audio(joke.response)
        joke.audio_url = await storage.save_audio(joke_id, audio_bytes)
        await db.commit()

    # For cloud storage, redirect to public URL
    if settings.use_cloud_storage:
        return Response(
            status_code=302,
            headers={"Location": joke.audio_url, "Cache-Control": "public, max-age=604800"}
        )
    
    # For local storage, serve the file
    audio_bytes = await storage.get_audio(joke.audio_url)
    if not audio_bytes:
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
    return {"ok": True}
