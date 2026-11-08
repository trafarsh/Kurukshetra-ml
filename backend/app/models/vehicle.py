"""Vehicle and vehicle configuration models."""
from __future__ import annotations

from typing import List, TYPE_CHECKING
from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.session import Session


class Vehicle(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "vehicles"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    chassis_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    engine_type: Mapped[str] = mapped_column(String(100), nullable=False)
    dry_mass_kg: Mapped[float] = mapped_column(Float, nullable=False)
    wheelbase_m: Mapped[float] = mapped_column(Float, nullable=False)
    track_width_m: Mapped[float] = mapped_column(Float, nullable=False)

    configurations: Mapped[List["VehicleConfiguration"]] = relationship(
        back_populates="vehicle", cascade="all, delete-orphan"
    )
    sessions: Mapped[List["Session"]] = relationship(back_populates="vehicle")


class VehicleConfiguration(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "vehicle_configurations"

    vehicle_id: Mapped[str] = mapped_column(ForeignKey("vehicles.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    drag_coefficient_cd: Mapped[float] = mapped_column(Float, nullable=False, default=0.65)
    frontal_area_m2: Mapped[float] = mapped_column(Float, nullable=False, default=0.42)
    rolling_resistance_crr: Mapped[float] = mapped_column(Float, nullable=False, default=0.018)
    engine_power_kw: Mapped[float] = mapped_column(Float, nullable=False, default=7.5)
    max_rpm: Mapped[int] = mapped_column(Integer, nullable=False, default=9500)
    gear_ratio: Mapped[float] = mapped_column(Float, nullable=False, default=4.2)

    vehicle: Mapped["Vehicle"] = relationship(back_populates="configurations")
    sessions: Mapped[List["Session"]] = relationship(back_populates="vehicle_configuration")

