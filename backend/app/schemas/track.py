"""Track and TrackSector schemas."""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class TrackSectorBase(BaseModel):
    sector_number: int
    start_distance_m: float
    end_distance_m: float
    is_corner: bool = False
    corner_radius_m: Optional[float] = None
    corner_direction: Optional[str] = None


class TrackSectorCreate(TrackSectorBase):
    pass


class TrackSectorResponse(TrackSectorBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    track_id: str


class TrackBase(BaseModel):
    name: str
    location: Optional[str] = None
    length_meters: float
    num_turns: int
    surface_type: str = "ASPHALT"
    centerline_geometry: Optional[str] = None


class TrackCreate(TrackBase):
    sectors: Optional[List[TrackSectorCreate]] = None


class TrackResponse(TrackBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    sectors: List[TrackSectorResponse] = []
