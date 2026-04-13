from contextlib import asynccontextmanager
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from core.config import get_settings
from core.database import engine, Base
from routers import jokes, share, gamify, battle, challenge, ws, heckle
from middleware.session import SessionMiddleware

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables + media dir
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    os.makedirs(settings.media_dir, exist_ok=True)
    os.makedirs(os.path.join(settings.media_dir, "audio"), exist_ok=True)

    # Start APScheduler for weekly challenge
    from tasks.scheduler import scheduler
    scheduler.start()

    yield

    # Shutdown
    scheduler.shutdown()
    await engine.dispose()


app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    lifespan=lifespan,
)

# CORS — allow Vite dev server + production domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Session cookie middleware
app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)

# Mount media files (TTS audio, card PNGs)
app.mount("/media", StaticFiles(directory=settings.media_dir), name="media")

# Routers
app.include_router(jokes.router)
app.include_router(share.router)
app.include_router(gamify.router)
app.include_router(battle.router)
app.include_router(challenge.router)
app.include_router(ws.router)
app.include_router(heckle.router)


@app.get("/api/health")
async def health():
    return {"status": "ok", "app": settings.app_name}
