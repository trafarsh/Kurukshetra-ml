"""Telemetry records, files, and alert models."""
from __future__ import annotations

from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import BigInteger, Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.session import Session


class TelemetryFile(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "telemetry_files"

    session_id: Mapped[str] = mapped_column(ForeignKey("sessions.id"), nullable=False, index=True)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_format: Mapped[str] = mapped_column(String(20), nullable=False)  # CSV or BINARY_16B
    file_size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    record_count: Mapped[int] = mapped_column(Integer, nullable=False)
    checksum_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    is_processed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    session: Mapped["Session"] = relationship(back_populates="telemetry_files")


class TelemetryRecord(Base):
    """Time-series sensor observations. High-frequency table."""
    __tablename__ = "telemetry_records"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String(36), ForeignKey("sessions.id"), nullable=False, index=True)
    lap_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("laps.id"), nullable=True, index=True)
    timestamp_us: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)

    speed_kmh: Mapped[float] = mapped_column(Float, nullable=False)
    engine_rpm: Mapped[int] = mapped_column(Integer, nullable=False)
    engine_temp_c: Mapped[float] = mapped_column(Float, nullable=False)
    steering_angle_deg: Mapped[float] = mapped_column(Float, nullable=False)
    throttle_percent: Mapped[float] = mapped_column(Float, nullable=False)
    accel_x_g: Mapped[float] = mapped_column(Float, nullable=False)
    accel_y_g: Mapped[float] = mapped_column(Float, nullable=False)
    accel_z_g: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    gyro_z_degps: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    obstacle_distance_cm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    closing_speed_mps: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    ttc_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    warning_level: Mapped[str] = mapped_column(String(20), default="SAFE", nullable=False)
    sensor_status: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class Alert(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "alerts"

    session_id: Mapped[str] = mapped_column(ForeignKey("sessions.id"), nullable=False, index=True)
    timestamp_us: Mapped[int] = mapped_column(BigInteger, nullable=False)
    alert_type: Mapped[str] = mapped_column(String(50), nullable=False)  # TTC_DANGER, ENGINE_OVERHEAT, etc.
    severity: Mapped[str] = mapped_column(String(20), nullable=False)    # INFO, WARNING, CRITICAL
    message: Mapped[str] = mapped_column(Text, nullable=False)
    acknowledged: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    session: Mapped["Session"] = relationship(back_populates="alerts")

