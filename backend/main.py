"""
FastAPI application entry-point.
"""
from contextlib import asynccontextmanager
import os
import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import redis.asyncio as aioredis
from sqlalchemy import text

from core.config import get_settings
from core.database import engine, Base
from core.logging import setup_logging, start_db_log_flush, stop_db_log_flush, get_logger
from routers import jokes, share, gamify, ws, heckle, logs
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

    # FIX Phase-3c: wait=True drains in-flight scheduled jobs before exit
    try:
        from tasks.scheduler import scheduler
        scheduler.shutdown(wait=True)
        await log.info("scheduler_stopped", "APScheduler stopped (drained)")
    except Exception as exc:
        await log.warning("scheduler_stop_failed", "APScheduler shutdown error", exc=exc)

    # FIX Phase-3d: close the singleton ARQ pool
    try:
        from workers.redis_client import close_arq_pool
        await close_arq_pool()
    except Exception as exc:
        await log.warning("arq_pool_close_failed", "ARQ pool close error", exc=exc)

    # FIX Phase-4: close Redis cache client
    try:
        from services.cache import close_cache
        await close_cache()
    except Exception as exc:
        await log.warning("cache_close_failed", "Cache Redis close error", exc=exc)

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
    try:
        response = await call_next(request)
        duration_ms = int((time.perf_counter() - start) * 1000)
        if response.status_code >= 400:
            await log.warning(
                "http_error_response",
                f"{request.method} {request.url.path} → {response.status_code}",
                details={"method": request.method, "path": request.url.path, "status_code": response.status_code},
                duration_ms=duration_ms,
            )
        else:
            await log.info(
                "http_request",
                f"{request.method} {request.url.path} → {response.status_code}",
                details={
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "client_ip": request.client.host if request.client else None,
                },
                duration_ms=duration_ms,
            )
        return response
    except Exception as exc:
        duration_ms = int((time.perf_counter() - start) * 1000)
        await log.error(
            "http_unhandled_exception",
            f"Unhandled exception on {request.method} {request.url.path}",
            duration_ms=duration_ms,
            exc=exc,
        )
        raise


# ── Static media ──────────────────────────────────────────────────────────────
if not settings.use_cloud_storage:
    app.mount("/media", StaticFiles(directory=settings.media_dir), name="media")

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(jokes.router)
app.include_router(share.router)
app.include_router(gamify.router)
app.include_router(ws.router)
app.include_router(heckle.router)
app.include_router(logs.router)


# ── Health — FIX Phase-3b: deep probes, returns 503 when deps are down ───────
@app.get("/api/health")
async def health():
    """
    Deep health check: probes the DB and Redis in addition to app liveness.
    Returns 200 {"status":"ok"} when all deps are healthy.
    Returns 503 {"status":"degraded",...} when any dep is unreachable.
    """
    checks: dict[str, str] = {}

    # DB probe
    try:
        from core.database import AsyncSessionLocal
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        checks["db"] = "ok"
    except Exception:
        checks["db"] = "error"

    # Redis probe
    try:
        r = aioredis.from_url(settings.redis_url, socket_connect_timeout=2)
        await r.ping()
        await r.aclose()
        checks["redis"] = "ok"
    except Exception:
        checks["redis"] = "error"

    all_ok = all(v == "ok" for v in checks.values())
    return JSONResponse(
        content={"status": "ok" if all_ok else "degraded", **checks},
        status_code=200 if all_ok else 503,
    )
