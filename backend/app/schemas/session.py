"""Session, Lap, Weather, and Setup schemas."""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class WeatherCreate(BaseModel):
    ambient_temp_c: float
    track_temp_c: Optional[float] = None
    relative_humidity_pct: float
    barometric_pressure_hpa: float
    air_density_kgm3: Optional[float] = 1.18
    track_condition: str = "DRY"


class WeatherResponse(WeatherCreate):
    model_config = ConfigDict(from_attributes=True)

    id: str
    session_id: str


class SetupCreate(BaseModel):
    tire_pressure_front_psi: float
    tire_pressure_rear_psi: float
    front_track_width_mm: float
    rear_track_width_mm: float
    gear_sprocket_teeth: int
    notes: Optional[str] = None


class SetupResponse(SetupCreate):
    model_config = ConfigDict(from_attributes=True)

    id: str
    session_id: str


class LapResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    session_id: str
    lap_number: int
    lap_time_s: float
    sector_1_time_s: Optional[float] = None
    sector_2_time_s: Optional[float] = None
    sector_3_time_s: Optional[float] = None
    max_speed_kmh: float
    min_speed_kmh: float
    avg_rpm: float
    max_lateral_g: float
    is_valid: bool


class SessionCreate(BaseModel):
    name: str
    track_id: str
    driver_id: str
    vehicle_id: str
    vehicle_config_id: str
    weather: Optional[WeatherCreate] = None
    setup: Optional[SetupCreate] = None


class SessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    date: datetime
    track_id: str
    driver_id: str
    vehicle_id: str
    vehicle_config_id: str
    status: str
    total_laps: int
    best_lap_time_s: Optional[float] = None
    avg_lap_time_s: Optional[float] = None
    created_at: datetime
    weather: Optional[WeatherResponse] = None
    setup: Optional[SetupResponse] = None
    laps: List[LapResponse] = []
