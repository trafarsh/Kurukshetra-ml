"""Driver schemas."""
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class DriverBase(BaseModel):
    name: str
    racing_number: int
    weight_kg: float
    experience_level: str = "COLLEGIATE"


class DriverCreate(DriverBase):
    pass


class DriverResponse(DriverBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
