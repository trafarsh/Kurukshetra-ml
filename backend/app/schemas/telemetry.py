"""Telemetry schemas."""
from typing import Any, Dict, Optional
from pydantic import BaseModel


class TelemetryIngestRequest(BaseModel):
    session_id: str
    timestamp_us: int
    speed_kmh: float
    engine_rpm: int
    engine_temp_c: float
    steering_angle_deg: float
    throttle_percent: float
    accel_x_g: float
    accel_y_g: float
    accel_z_g: Optional[float] = None
    gyro_z_degps: Optional[float] = None
    obstacle_distance_cm: Optional[float] = None
    closing_speed_mps: Optional[float] = None
    ttc_seconds: Optional[float] = None
    warning_level: str = "SAFE"
    sensor_status: Optional[str] = None


class TelemetryImportResponse(BaseModel):
    file_id: str
    session_id: str
    records_parsed: int
    duration_seconds: float
    data_quality: Dict[str, Any]
    laps_detected: int


class TelemetrySummaryResponse(BaseModel):
    session_id: str
    record_count: int
    max_speed_kmh: float
    avg_speed_kmh: float
    max_rpm: int
    max_temp_c: float
    max_lateral_g: float
    active_warnings_count: int

