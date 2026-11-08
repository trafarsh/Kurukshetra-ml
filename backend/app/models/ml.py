"""Machine Learning registry and experiment tracking models."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class MLModel(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "ml_models"

    model_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    algorithm: Mapped[str] = mapped_column(String(100), nullable=False)
    hyperparameters: Mapped[str] = mapped_column(Text, nullable=False)  # JSON
    artifact_path: Mapped[str] = mapped_column(String(500), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    trained_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    experiments: Mapped[List["MLExperiment"]] = relationship(back_populates="model", cascade="all, delete-orphan")
    predictions: Mapped[List["MLPrediction"]] = relationship(back_populates="model")


class MLExperiment(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "ml_experiments"

    model_id: Mapped[str] = mapped_column(ForeignKey("ml_models.id"), nullable=False, index=True)
    dataset_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    train_records_count: Mapped[int] = mapped_column(Integer, nullable=False)
    test_records_count: Mapped[int] = mapped_column(Integer, nullable=False)
    mae: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    rmse: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    r2_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    f1_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    evaluation_summary: Mapped[str] = mapped_column(Text, nullable=False)  # JSON
    executed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    model: Mapped["MLModel"] = relationship(back_populates="experiments")


class MLPrediction(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "ml_predictions"

    model_id: Mapped[str] = mapped_column(ForeignKey("ml_models.id"), nullable=False, index=True)
    session_id: Mapped[str] = mapped_column(String(36), ForeignKey("sessions.id"), nullable=False, index=True)
    lap_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("laps.id"), nullable=True)
    input_features: Mapped[str] = mapped_column(Text, nullable=False)  # JSON
    prediction_value: Mapped[float] = mapped_column(Float, nullable=False)
    confidence_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    anomaly_flag: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    model: Mapped["MLModel"] = relationship(back_populates="predictions")

