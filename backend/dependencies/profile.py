from datetime import date
from fastapi import Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.database import get_db
from models.profile import UserProfile


async def get_profile(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> UserProfile:
    session_id = getattr(request.state, "session_id", None)
    if not session_id:
        # Return a transient dummy profile for unauthenticated requests
        return UserProfile(session_key="anonymous", xp=0, streak=0)

    result = await db.execute(
        select(UserProfile).where(UserProfile.session_key == session_id)
    )
    profile = result.scalar_one_or_none()

    if not profile:
        profile = UserProfile(session_key=session_id)
        db.add(profile)
        await db.flush()

    today = date.today()
    if profile.last_visit != today:
        if profile.last_visit and (today - profile.last_visit).days == 1:
            profile.streak += 1
        elif profile.last_visit and (today - profile.last_visit).days > 1:
            profile.streak = 1
        else:
            profile.streak = max(1, profile.streak)
        profile.last_visit = today
        profile.xp += 5     # daily visit XP

    return profile
