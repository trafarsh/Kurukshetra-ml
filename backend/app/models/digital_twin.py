"""Digital Twin configurations, simulation runs, and calibration records."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from sqlalchemy import BigInteger, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class DigitalTwinConfig(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "digital_twin_configs"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    kart_mass_kg: Mapped[float] = mapped_column(Float, nullable=False, default=175.0)  # Kart + Driver
    effective_grip_mu: Mapped[float] = mapped_column(Float, nullable=False, default=1.15)
    aerodynamic_cd: Mapped[float] = mapped_column(Float, nullable=False, default=0.65)
    frontal_area_m2: Mapped[float] = mapped_column(Float, nullable=False, default=0.42)
    rolling_resistance: Mapped[float] = mapped_column(Float, nullable=False, default=0.018)
    peak_power_kw: Mapped[float] = mapped_column(Float, nullable=False, default=7.5)

    simulation_runs: Mapped[List["SimulationRun"]] = relationship(back_populates="config", cascade="all, delete-orphan")


class SimulationRun(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "simulation_runs"

    config_id: Mapped[str] = mapped_column(ForeignKey("digital_twin_configs.id"), nullable=False, index=True)
    session_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("sessions.id"), nullable=True)
    run_type: Mapped[str] = mapped_column(String(50), nullable=False, default="BASELINE")  # BASELINE, CALIBRATION, WHAT_IF
    scenario_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    simulated_lap_time_s: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="SUCCESS", nullable=False)
    executed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    config: Mapped["DigitalTwinConfig"] = relationship(back_populates="simulation_runs")
    results: Mapped[List["SimulationResult"]] = relationship(back_populates="simulation_run", cascade="all, delete-orphan")
    calibration_record: Mapped[Optional["CalibrationRecord"]] = relationship(back_populates="simulation_run", uselist=False)


class SimulationResult(Base):
    """Trajectory trace from physics solver."""
    __tablename__ = "simulation_results"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    simulation_run_id: Mapped[str] = mapped_column(String(36), ForeignKey("simulation_runs.id"), nullable=False, index=True)
    distance_m: Mapped[float] = mapped_column(Float, nullable=False)
    simulated_speed_kmh: Mapped[float] = mapped_column(Float, nullable=False)
    simulated_accel_x_g: Mapped[float] = mapped_column(Float, nullable=False)
    simulated_accel_y_g: Mapped[float] = mapped_column(Float, nullable=False)
    limiting_constraint: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # POWER, GRIP, BRAKING

    simulation_run: Mapped["SimulationRun"] = relationship(back_populates="results")


class CalibrationRecord(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "calibration_records"

    simulation_run_id: Mapped[str] = mapped_column(ForeignKey("simulation_runs.id"), unique=True, nullable=False)
    reference_lap_id: Mapped[str] = mapped_column(String(36), ForeignKey("laps.id"), nullable=False)
    initial_grip_mu: Mapped[float] = mapped_column(Float, nullable=False)
    calibrated_grip_mu: Mapped[float] = mapped_column(Float, nullable=False)
    initial_rmse_kmh: Mapped[float] = mapped_column(Float, nullable=False)
    final_rmse_kmh: Mapped[float] = mapped_column(Float, nullable=False)
    iterations: Mapped[int] = mapped_column(Integer, nullable=False)
    calibrated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    simulation_run: Mapped["SimulationRun"] = relationship(back_populates="calibration_record")

