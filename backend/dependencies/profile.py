from fastapi import Request, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.database import get_db
from models.profile import UserProfile

async def get_profile(request: Request, db: AsyncSession = Depends(get_db)) -> UserProfile:
    session_id = request.session.get("session_id")
    if not session_id:
        # For simplicity, we create a session if it doesn't exist or handle it in middleware
        # But here we expect the middleware to have set it.
        raise HTTPException(status_code=401, detail="Session not initialized")
    
    result = await db.execute(select(UserProfile).where(UserProfile.id == session_id))
    profile = result.scalar_one_or_none()
    
    if not profile:
        profile = UserProfile(id=session_id)
        db.add(profile)
        await db.commit()
        await db.refresh(profile)
        
    return profile
