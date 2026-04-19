from contextlib import asynccontextmanager
import os
import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from core.config import get_settings
from core.database import engine, Base
from core.logging import setup_logging, start_db_log_flush, stop_db_log_flush, get_logger
from routers import jokes, share, gamify, battle, challenge, ws, heckle, logs
from middleware.session import SessionMiddleware

settings = get_settings()
log = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ──────────────────────────────────────────────────────────────
    setup_logging(log_level="DEBUG" if settings.debug else "INFO")
    start_db_log_flush()

    await log.info(
        "app_startup",
        f"Starting {settings.app_name}",
        details={
            "debug": settings.debug,
            "database": settings.database_url.split("@")[-1] if "@" in settings.database_url else "local",
            "cloud_storage": settings.use_cloud_storage,
            "cors_origins": settings.cors_origins,
        },
    )

    # Create tables + media dir
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        await log.info("db_tables_ready", "Database tables verified / created")
    except Exception as exc:
        await log.critical("db_init_failed", "Failed to initialise database tables", exc=exc)
        raise

    if not settings.use_cloud_storage:
        os.makedirs(settings.media_dir, exist_ok=True)
        os.makedirs(os.path.join(settings.media_dir, "audio"), exist_ok=True)
        await log.info("media_dir_ready", f"Local media directory ready: {settings.media_dir}")

    # Start APScheduler
    try:
        from tasks.scheduler import scheduler
        scheduler.start()
        await log.info("scheduler_started", "APScheduler started")
    except Exception as exc:
        await log.error("scheduler_start_failed", "APScheduler failed to start", exc=exc)

    await log.info("app_ready", f"{settings.app_name} is ready to serve requests")

    yield

    # ── Shutdown ─────────────────────────────────────────────────────────────
    await log.info("app_shutdown", f"Shutting down {settings.app_name}")

    try:
        from tasks.scheduler import scheduler
        scheduler.shutdown()
        await log.info("scheduler_stopped", "APScheduler stopped")
    except Exception as exc:
        await log.warning("scheduler_stop_failed", "APScheduler shutdown error", exc=exc)

    await engine.dispose()
    await log.info("db_engine_disposed", "Database engine disposed")

    stop_db_log_flush()


app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    lifespan=lifespan,
)

# ── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Session cookie middleware ─────────────────────────────────────────────────
app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)

# ── Request / response timing middleware ─────────────────────────────────────
@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    start = time.perf_counter()
    response = None
    try:
        response = await call_next(request)
        duration_ms = int((time.perf_counter() - start) * 1000)
        level = "WARNING" if response.status_code >= 400 else "INFO"
        await log.info(
            "http_request",
            f"{request.method} {request.url.path} → {response.status_code}",
            details={
                "method": request.method,
                "path": request.url.path,
                "query": str(request.url.query) or None,
                "status_code": response.status_code,
                "client_ip": request.client.host if request.client else None,
            },
            duration_ms=duration_ms,
        ) if level == "INFO" else await log.warning(
            "http_error_response",
            f"{request.method} {request.url.path} → {response.status_code}",
            details={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
            },
            duration_ms=duration_ms,
        )
        return response
    except Exception as exc:
        duration_ms = int((time.perf_counter() - start) * 1000)
        await log.error(
            "http_unhandled_exception",
            f"Unhandled exception on {request.method} {request.url.path}",
            details={"method": request.method, "path": request.url.path},
            duration_ms=duration_ms,
            exc=exc,
        )
        raise


# ── Static media (local storage only) ────────────────────────────────────────
if not settings.use_cloud_storage:
    app.mount("/media", StaticFiles(directory=settings.media_dir), name="media")

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(jokes.router)
app.include_router(share.router)
app.include_router(gamify.router)
app.include_router(battle.router)
app.include_router(challenge.router)
app.include_router(ws.router)
app.include_router(heckle.router)
app.include_router(logs.router)


@app.get("/api/health")
async def health():
    await log.debug("health_check", "Health check endpoint called")
    return {"status": "ok", "app": settings.app_name}
