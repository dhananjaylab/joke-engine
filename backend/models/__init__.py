# Import all models for Alembic auto-detection
from .joke import Joke
from .profile import UserProfile
from .daily_joke import DailyJoke

__all__ = ["Joke", "UserProfile", "DailyJoke"]
