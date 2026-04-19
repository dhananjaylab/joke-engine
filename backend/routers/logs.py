"""
Admin log viewer — query app_logs from Neon PostgreSQL.

Endpoints
---------
GET /api/logs          — paginated log list with filters
GET /api/logs/stats    — aggregate counts by level and event
GET /api/logs/{log_id} — single log entry with full traceback
"""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc

from core.database import get_db
from core.logging import get_logger
from models.app_log import AppLog

router = APIRouter(prefix="/api/logs", tags=["logs"])
log = get_logger("routers.logs")


@router.get("")
async def list_logs(
    level: Optional[str] = Query(None, description="Filter by level: DEBUG/INFO/WARNING/ERROR/CRITICAL"),
    event: Optional[str] = Query(None, description="Filter by event key (partial match)"),
    logger_name: Optional[str] = Query(None, description="Filter by logger name (partial match)"),
    session_key: Optional[str] = Query(None, description="Filter by session key"),
    joke_id: Optional[int] = Query(None, description="Filter by joke ID"),
    since: Optional[datetime] = Query(None, description="ISO datetime lower bound"),
    until: Optional[datetime] = Query(None, description="ISO datetime upper bound"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """
    Paginated log query with optional filters.
    Results are ordered newest-first.
    """
    query = select(AppLog)

    if level:
        query = query.where(AppLog.level == level.upper())
    if event:
        query = query.where(AppLog.event.ilike(f"%{event}%"))
    if logger_name:
        query = query.where(AppLog.logger_name.ilike(f"%{logger_name}%"))
    if session_key:
        query = query.where(AppLog.session_key == session_key)
    if joke_id is not None:
        query = query.where(AppLog.joke_id == joke_id)
    if since:
        query = query.where(AppLog.created_at >= since)
    if until:
        query = query.where(AppLog.created_at <= until)

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    # Paginate
    offset = (page - 1) * page_size
    query = query.order_by(desc(AppLog.created_at)).offset(offset).limit(page_size)
    result = await db.execute(query)
    entries = result.scalars().all()

    return {
        "total": total,
        "page": page,
        "pages": -(-total // page_size),
        "page_size": page_size,
        "logs": [
            {
                "id": e.id,
                "level": e.level,
                "logger_name": e.logger_name,
                "event": e.event,
                "message": e.message,
                "details": e.details,
                "session_key": e.session_key,
                "joke_id": e.joke_id,
                "duration_ms": e.duration_ms,
                "error": e.error,
                "created_at": e.created_at.isoformat() if e.created_at else None,
            }
            for e in entries
        ],
    }


@router.get("/stats")
async def log_stats(
    since: Optional[datetime] = Query(None, description="ISO datetime lower bound"),
    db: AsyncSession = Depends(get_db),
):
    """
    Aggregate log counts grouped by level and top events.
    """
    base = select(AppLog)
    if since:
        base = base.where(AppLog.created_at >= since)

    # Counts by level
    level_q = (
        select(AppLog.level, func.count(AppLog.id).label("count"))
        .where(AppLog.created_at >= since if since else True)
        .group_by(AppLog.level)
        .order_by(desc("count"))
    )
    level_result = await db.execute(level_q)
    by_level = {row.level: row.count for row in level_result}

    # Top 20 events
    event_q = (
        select(AppLog.event, func.count(AppLog.id).label("count"))
        .where(AppLog.created_at >= since if since else True)
        .group_by(AppLog.event)
        .order_by(desc("count"))
        .limit(20)
    )
    event_result = await db.execute(event_q)
    top_events = [{"event": row.event, "count": row.count} for row in event_result]

    # Error count in last 24h
    from datetime import timezone, timedelta
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    error_q = select(func.count(AppLog.id)).where(
        AppLog.level.in_(["ERROR", "CRITICAL"]),
        AppLog.created_at >= cutoff,
    )
    error_result = await db.execute(error_q)
    errors_24h = error_result.scalar_one()

    return {
        "by_level": by_level,
        "top_events": top_events,
        "errors_last_24h": errors_24h,
    }


@router.get("/{log_id}")
async def get_log_entry(log_id: int, db: AsyncSession = Depends(get_db)):
    """Fetch a single log entry including full traceback."""
    result = await db.execute(select(AppLog).where(AppLog.id == log_id))
    entry = result.scalar_one_or_none()
    if not entry:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Log entry not found")

    return {
        "id": entry.id,
        "level": entry.level,
        "logger_name": entry.logger_name,
        "event": entry.event,
        "message": entry.message,
        "details": entry.details,
        "session_key": entry.session_key,
        "joke_id": entry.joke_id,
        "duration_ms": entry.duration_ms,
        "error": entry.error,
        "traceback": entry.traceback,
        "created_at": entry.created_at.isoformat() if entry.created_at else None,
    }
