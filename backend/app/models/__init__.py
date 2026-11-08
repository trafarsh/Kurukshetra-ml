"""
SQLAlchemy models for Kurukshetra Kart.

All models are imported here so that Base.metadata is aware of every table
when init_db() calls Base.metadata.create_all().
"""
from app.models.base import TimestampMixin, UUIDMixin  # noqa: F401
from app.models.user import Role, User  # noqa: F401
from app.models.driver import Driver  # noqa: F401
from app.models.vehicle import Vehicle, VehicleConfiguration  # noqa: F401
from app.models.track import Track, TrackSector  # noqa: F401
from app.models.session import Session, Lap, WeatherCondition, SetupConfiguration  # noqa: F401
from app.models.telemetry import TelemetryFile, TelemetryRecord, Alert  # noqa: F401
from app.models.ml import MLModel, MLExperiment, MLPrediction  # noqa: F401
from app.models.digital_twin import (  # noqa: F401
    DigitalTwinConfig,
    SimulationRun,
    SimulationResult,
    CalibrationRecord,
)
from app.models.report import Report  # noqa: F401
