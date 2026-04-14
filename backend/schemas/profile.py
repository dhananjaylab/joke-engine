from pydantic import BaseModel


class ProfileResponse(BaseModel):
    xp: int
    streak: int
    rank: str

    class Config:
        from_attributes = True
