from fastapi import APIRouter, Depends
from models.profile import UserProfile
from dependencies.profile import get_profile

router = APIRouter(prefix="/api/gamify", tags=["gamify"])

@router.get("/profile")
async def read_profile(profile: UserProfile = Depends(get_profile)):
    return {
        "xp": profile.xp,
        "streak": profile.streak_count,
        "last_active": profile.last_active
    }
