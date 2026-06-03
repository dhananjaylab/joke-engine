"""
Typed error envelope for all HTTP error responses.

FIX Phase-4: Previously all HTTPException details were free-form strings,
forcing clients to string-match error messages. This schema gives each
error a stable machine-readable code and is automatically reflected in
the generated OpenAPI spec.

Usage:
    from schemas.errors import AppError, raise_app_error

    raise_app_error(503, "ai_unavailable", "AI service is temporarily unavailable")
"""
from __future__ import annotations

from typing import Literal

from fastapi import HTTPException
from pydantic import BaseModel

ErrorCode = Literal[
    "ai_unavailable",
    "audio_failed",
    "card_failed",
    "jotd_unavailable",
    "joke_not_found",
    "random_joke_failed",
    "rate_limited",
    "validation_error",
]


class AppError(BaseModel):
    code: ErrorCode
    message: str
    details: dict | None = None


def raise_app_error(
    status_code: int,
    code: ErrorCode,
    message: str,
    details: dict | None = None,
) -> None:
    """Raise an HTTPException with a typed AppError detail payload."""
    raise HTTPException(
        status_code=status_code,
        detail=AppError(code=code, message=message, details=details).model_dump(),
    )
