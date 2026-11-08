"""
Database engine, session factory, Base class, and initialisation helpers.
"""
from __future__ import annotations

from collections.abc import Generator
from typing import Any

from sqlalchemy import event, create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings


# ── Engine ────────────────────────────────────────────────────────────────────
connect_args: dict[str, Any] = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=settings.DEBUG,
    pool_pre_ping=True,
)

# Enable WAL journal mode for SQLite so concurrent readers don't block writers.
if settings.DATABASE_URL.startswith("sqlite"):

    @event.listens_for(engine, "connect")
    def _set_sqlite_wal(dbapi_connection: Any, _connection_record: Any) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL;")
        cursor.close()


# ── Session factory ───────────────────────────────────────────────────────────
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


# ── Declarative Base ─────────────────────────────────────────────────────────
class Base(DeclarativeBase):
    """Application-wide declarative base for all ORM models."""
    pass


# ── Dependency ────────────────────────────────────────────────────────────────
def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a database session and ensures cleanup."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── Bootstrap ─────────────────────────────────────────────────────────────────
def init_db() -> None:
    """Create all tables registered with *Base.metadata*.

    Must be called **after** every model module has been imported so that the
    metadata registry is fully populated.
    """
    # The models __init__.py imports every model → Base.metadata is complete.
    import app.models  # noqa: F401

    Base.metadata.create_all(bind=engine)
