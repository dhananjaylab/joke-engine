from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from dependencies.profile import get_profile
from models.profile import UserProfile
from schemas.profile import ProfileResponse

router = APIRouter(prefix="/api", tags=["gamify"])


@router.get("/profile", response_model=ProfileResponse)
async def get_my_profile(
    profile: UserProfile = Depends(get_profile),
    db: AsyncSession = Depends(get_db),
):
    await db.commit()   # flush streak/XP updates from middleware
    return profile
