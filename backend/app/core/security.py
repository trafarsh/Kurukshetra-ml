"""
Password hashing and JWT token utilities.
"""
from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt

from app.core.config import settings

# ── Constant salt prefix (per-deployment) ────────────────────────────────────
_SALT_LENGTH = 32


# ── Password helpers ─────────────────────────────────────────────────────────
def hash_password(password: str) -> str:
    """Return a salted SHA-256 hash in the format ``<salt>$<hex-digest>``."""
    salt = secrets.token_hex(_SALT_LENGTH)
    digest = hashlib.sha256(f"{salt}{password}".encode()).hexdigest()
    return f"{salt}${digest}"


def verify_password(plain: str, hashed: str) -> bool:
    """Verify *plain* against a hash produced by :func:`hash_password`."""
    try:
        salt, digest = hashed.split("$", 1)
    except ValueError:
        return False
    expected = hashlib.sha256(f"{salt}{plain}".encode()).hexdigest()
    return secrets.compare_digest(expected, digest)


# ── JWT helpers ──────────────────────────────────────────────────────────────
_ALGORITHM = "HS256"


def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """Create a signed JWT containing *data* as claims."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=_ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any]:
    """Decode and verify a JWT.  Raises ``jwt.PyJWTError`` on failure."""
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[_ALGORITHM])
