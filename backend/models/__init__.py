# Import all models for Alembic auto-detection
from .joke import Joke
from .profile import UserProfile
from .daily_joke import DailyJoke
from .app_log import AppLog

__all__ = ["Joke", "UserProfile", "DailyJoke", "AppLog"]
