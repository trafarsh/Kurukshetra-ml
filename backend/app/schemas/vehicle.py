"""Vehicle and configuration schemas."""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class VehicleConfigBase(BaseModel):
    name: str
    drag_coefficient_cd: float = 0.65
    frontal_area_m2: float = 0.42
    rolling_resistance_crr: float = 0.018
    engine_power_kw: float = 7.5
    max_rpm: int = 9500
    gear_ratio: float = 4.2


class VehicleConfigCreate(VehicleConfigBase):
    pass


class VehicleConfigResponse(VehicleConfigBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    vehicle_id: str
    created_at: datetime


class VehicleBase(BaseModel):
    name: str
    chassis_code: str
    engine_type: str
    dry_mass_kg: float
    wheelbase_m: float
    track_width_m: float


class VehicleCreate(VehicleBase):
    configurations: Optional[List[VehicleConfigCreate]] = None


class VehicleUpdate(BaseModel):
    name: Optional[str] = None
    dry_mass_kg: Optional[float] = None
    wheelbase_m: Optional[float] = None
    track_width_m: Optional[float] = None


class VehicleResponse(VehicleBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    configurations: List[VehicleConfigResponse] = []
