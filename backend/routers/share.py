import os
import hashlib
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse, FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.database import get_db
from core.config import get_settings
from models.joke import Joke
from services.ai import generate_audio
from services.image import render_joke_card

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

    if not joke.audio_url:
        audio_bytes = await generate_audio(joke.response)
        filename = f"joke_{joke_id}_{hashlib.md5(joke.response.encode()).hexdigest()[:8]}.mp3"
        path = os.path.join(settings.media_dir, "audio", filename)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(audio_bytes)
        joke.audio_url = f"/media/audio/{filename}"
        await db.commit()

    return FileResponse(
        path=os.path.join(settings.media_dir, "audio", os.path.basename(joke.audio_url)),
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
