"""Driver profile model."""
from __future__ import annotations

from typing import List, TYPE_CHECKING
from sqlalchemy import Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.session import Session


class Driver(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "drivers"

    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    racing_number: Mapped[int] = mapped_column(Integer, nullable=False)
    weight_kg: Mapped[float] = mapped_column(Float, nullable=False)
    experience_level: Mapped[str] = mapped_column(String(50), default="COLLEGIATE", nullable=False)

    sessions: Mapped[List["Session"]] = relationship(back_populates="driver")

