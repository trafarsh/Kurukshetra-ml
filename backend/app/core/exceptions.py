"""
Application-specific exceptions and the FastAPI exception handler.
"""
from __future__ import annotations

from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse


# ── Base exception ───────────────────────────────────────────────────────────
class KartException(Exception):
    """Base exception for all Kurukshetra Kart domain errors."""

    def __init__(
        self,
        status_code: int = 500,
        code: str = "INTERNAL_ERROR",
        message: str = "An unexpected error occurred.",
        details: Any = None,
    ) -> None:
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details
        super().__init__(message)


# ── Concrete exceptions ─────────────────────────────────────────────────────
class EntityNotFoundError(KartException):
    """Raised when a requested entity does not exist."""

    def __init__(self, entity: str = "Entity", entity_id: str = "") -> None:
        super().__init__(
            status_code=404,
            code="NOT_FOUND",
            message=f"{entity} with id '{entity_id}' not found.",
        )


class ValidationError(KartException):
    """Raised when input validation fails beyond Pydantic checks."""

    def __init__(self, message: str = "Validation failed.", details: Any = None) -> None:
        super().__init__(
            status_code=422,
            code="VALIDATION_ERROR",
            message=message,
            details=details,
        )


class AuthenticationError(KartException):
    """Raised when authentication fails (bad credentials or token)."""

    def __init__(self, message: str = "Authentication failed.") -> None:
        super().__init__(
            status_code=401,
            code="AUTHENTICATION_ERROR",
            message=message,
        )


# ── FastAPI handler ──────────────────────────────────────────────────────────
async def kart_exception_handler(_request: Request, exc: KartException) -> JSONResponse:
    """Convert a :class:`KartException` into a structured JSON response."""
    body: dict[str, Any] = {
        "error": {
            "code": exc.code,
            "message": exc.message,
        }
    }
    if exc.details is not None:
        body["error"]["details"] = exc.details
    return JSONResponse(status_code=exc.status_code, content=body)
