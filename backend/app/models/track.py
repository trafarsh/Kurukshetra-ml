"""Track and TrackSector models."""
from __future__ import annotations

from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import Boolean, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.session import Session


class Track(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "tracks"

    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    location: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    length_meters: Mapped[float] = mapped_column(Float, nullable=False)
    num_turns: Mapped[int] = mapped_column(Integer, nullable=False)
    surface_type: Mapped[str] = mapped_column(String(50), default="ASPHALT", nullable=False)
    centerline_geometry: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    sectors: Mapped[List["TrackSector"]] = relationship(
        back_populates="track", cascade="all, delete-orphan", order_by="TrackSector.sector_number"
    )
    sessions: Mapped[List["Session"]] = relationship(back_populates="track")


class TrackSector(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "track_sectors"

    track_id: Mapped[str] = mapped_column(ForeignKey("tracks.id"), nullable=False)
    sector_number: Mapped[int] = mapped_column(Integer, nullable=False)
    start_distance_m: Mapped[float] = mapped_column(Float, nullable=False)
    end_distance_m: Mapped[float] = mapped_column(Float, nullable=False)
    is_corner: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    corner_radius_m: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    corner_direction: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)

    track: Mapped["Track"] = relationship(back_populates="sectors")

