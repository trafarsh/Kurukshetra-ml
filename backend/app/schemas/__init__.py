"""Pydantic schemas package."""
from app.schemas.common import StatusResponse, ErrorResponse, PaginatedResponse
from app.schemas.auth import LoginRequest, TokenResponse, UserPublic, UserCreate
from app.schemas.vehicle import VehicleCreate, VehicleUpdate, VehicleResponse, VehicleConfigCreate, VehicleConfigResponse
from app.schemas.driver import DriverCreate, DriverResponse
from app.schemas.track import TrackCreate, TrackResponse, TrackSectorCreate, TrackSectorResponse
from app.schemas.session import SessionCreate, SessionResponse, LapResponse, WeatherCreate, SetupCreate
from app.schemas.telemetry import TelemetryIngestRequest, TelemetryImportResponse, TelemetrySummaryResponse

__all__ = [
    "StatusResponse", "ErrorResponse", "PaginatedResponse",
    "LoginRequest", "TokenResponse", "UserPublic", "UserCreate",
    "VehicleCreate", "VehicleUpdate", "VehicleResponse", "VehicleConfigCreate", "VehicleConfigResponse",
    "DriverCreate", "DriverResponse",
    "TrackCreate", "TrackResponse", "TrackSectorCreate", "TrackSectorResponse",
    "SessionCreate", "SessionResponse", "LapResponse", "WeatherCreate", "SetupCreate",
    "TelemetryIngestRequest", "TelemetryImportResponse", "TelemetrySummaryResponse",
]
