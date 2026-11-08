"""Session, Lap, WeatherCondition, and SetupConfiguration models."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.driver import Driver
    from app.models.vehicle import Vehicle, VehicleConfiguration
    from app.models.track import Track
    from app.models.telemetry import TelemetryFile, TelemetryRecord, Alert
    from app.models.report import Report


class Session(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "sessions"

    name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    track_id: Mapped[str] = mapped_column(ForeignKey("tracks.id"), nullable=False)
    driver_id: Mapped[str] = mapped_column(ForeignKey("drivers.id"), nullable=False)
    vehicle_id: Mapped[str] = mapped_column(ForeignKey("vehicles.id"), nullable=False)
    vehicle_config_id: Mapped[str] = mapped_column(ForeignKey("vehicle_configurations.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="ACTIVE", nullable=False)
    total_laps: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    best_lap_time_s: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    avg_lap_time_s: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    created_by: Mapped[str] = mapped_column(String(36), nullable=False)

    driver: Mapped["Driver"] = relationship(back_populates="sessions")
    vehicle: Mapped["Vehicle"] = relationship(back_populates="sessions")
    vehicle_configuration: Mapped["VehicleConfiguration"] = relationship(back_populates="sessions")
    track: Mapped["Track"] = relationship(back_populates="sessions")

    laps: Mapped[List["Lap"]] = relationship(back_populates="session", cascade="all, delete-orphan", order_by="Lap.lap_number")
    weather: Mapped[Optional["WeatherCondition"]] = relationship(back_populates="session", uselist=False, cascade="all, delete-orphan")
    setup: Mapped[Optional["SetupConfiguration"]] = relationship(back_populates="session", uselist=False, cascade="all, delete-orphan")
    telemetry_files: Mapped[List["TelemetryFile"]] = relationship(back_populates="session", cascade="all, delete-orphan")
    alerts: Mapped[List["Alert"]] = relationship(back_populates="session", cascade="all, delete-orphan")
    reports: Mapped[List["Report"]] = relationship(back_populates="session", cascade="all, delete-orphan")


class Lap(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "laps"

    session_id: Mapped[str] = mapped_column(ForeignKey("sessions.id"), nullable=False, index=True)
    lap_number: Mapped[int] = mapped_column(Integer, nullable=False)
    lap_time_s: Mapped[float] = mapped_column(Float, nullable=False)
    sector_1_time_s: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    sector_2_time_s: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    sector_3_time_s: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    max_speed_kmh: Mapped[float] = mapped_column(Float, nullable=False)
    min_speed_kmh: Mapped[float] = mapped_column(Float, nullable=False)
    avg_rpm: Mapped[float] = mapped_column(Float, nullable=False)
    max_lateral_g: Mapped[float] = mapped_column(Float, nullable=False)
    is_valid: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    session: Mapped["Session"] = relationship(back_populates="laps")


class WeatherCondition(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "weather_conditions"

    session_id: Mapped[str] = mapped_column(ForeignKey("sessions.id"), unique=True, nullable=False)
    ambient_temp_c: Mapped[float] = mapped_column(Float, nullable=False)
    track_temp_c: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    relative_humidity_pct: Mapped[float] = mapped_column(Float, nullable=False)
    barometric_pressure_hpa: Mapped[float] = mapped_column(Float, nullable=False)
    air_density_kgm3: Mapped[float] = mapped_column(Float, nullable=False)
    track_condition: Mapped[str] = mapped_column(String(30), default="DRY", nullable=False)

    session: Mapped["Session"] = relationship(back_populates="weather")


class SetupConfiguration(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "setup_configurations"

    session_id: Mapped[str] = mapped_column(ForeignKey("sessions.id"), unique=True, nullable=False)
    tire_pressure_front_psi: Mapped[float] = mapped_column(Float, nullable=False)
    tire_pressure_rear_psi: Mapped[float] = mapped_column(Float, nullable=False)
    front_track_width_mm: Mapped[float] = mapped_column(Float, nullable=False)
    rear_track_width_mm: Mapped[float] = mapped_column(Float, nullable=False)
    gear_sprocket_teeth: Mapped[int] = mapped_column(Integer, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    session: Mapped["Session"] = relationship(back_populates="setup")

