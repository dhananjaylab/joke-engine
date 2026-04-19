import time
from datetime import date
from fastapi import Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.database import get_db
from core.logging import get_logger
from models.profile import UserProfile

log = get_logger("dependencies.profile")


async def get_profile(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> UserProfile:
    session_id = getattr(request.state, "session_id", None)

    if not session_id:
        await log.warning(
            "profile_no_session",
            "Request has no session_id — returning anonymous profile",
            details={"path": request.url.path},
        )
        return UserProfile(session_key="anonymous", xp=0, streak=0)

    start = time.perf_counter()

    result = await db.execute(
        select(UserProfile).where(UserProfile.session_key == session_id)
    )
    profile = result.scalar_one_or_none()

    if not profile:
        profile = UserProfile(session_key=session_id)
        db.add(profile)
        await db.flush()
        duration_ms = int((time.perf_counter() - start) * 1000)
        await log.info(
            "profile_created",
            f"New user profile created for session {session_id[:8]}…",
            session_key=session_id,
            duration_ms=duration_ms,
            details={"session_key": session_id},
        )
    else:
        await log.debug(
            "profile_loaded",
            f"Profile loaded for session {session_id[:8]}… (xp={profile.xp} streak={profile.streak})",
            session_key=session_id,
            details={"xp": profile.xp, "streak": profile.streak, "rank": profile.rank},
        )

    today = date.today()
    if profile.last_visit != today:
        old_streak = profile.streak
        if profile.last_visit and (today - profile.last_visit).days == 1:
            profile.streak += 1
        elif profile.last_visit and (today - profile.last_visit).days > 1:
            profile.streak = 1
        else:
            profile.streak = max(1, profile.streak)
        profile.last_visit = today
        profile.xp += 5  # daily visit XP

        await log.info(
            "profile_daily_visit",
            f"Daily visit recorded for session {session_id[:8]}… — streak {old_streak}→{profile.streak} xp+5",
            session_key=session_id,
            details={
                "old_streak": old_streak,
                "new_streak": profile.streak,
                "xp": profile.xp,
                "last_visit": str(today),
            },
        )

    return profile
