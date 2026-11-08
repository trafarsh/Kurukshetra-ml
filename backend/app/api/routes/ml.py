"""Machine-learning inference endpoints."""
from typing import List

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.services.anomaly_detector import anomaly_service

router = APIRouter(prefix="/ml", tags=["Machine Learning"])


class EngineAnomalyRequest(BaseModel):
    rpm: float = Field(ge=0)
    temp_c: float
    speed_kmh: float = Field(ge=0)
    accel_x_g: float


class EngineAnomalyResponse(BaseModel):
    is_anomaly: bool
    anomaly_score: float
    model_version: str


class EngineAnomalyTrainingRequest(BaseModel):
    samples: List[List[float]] = Field(min_length=10)


@router.post("/anomaly/predict", response_model=EngineAnomalyResponse)
def predict_engine_anomaly(payload: EngineAnomalyRequest) -> EngineAnomalyResponse:
    result = anomaly_service.predict(payload.rpm, payload.temp_c, payload.speed_kmh, payload.accel_x_g)
    return EngineAnomalyResponse(
        is_anomaly=result.is_anomaly,
        anomaly_score=result.anomaly_score,
        model_version=result.model_version,
    )


@router.post("/anomaly/train", status_code=status.HTTP_201_CREATED)
def train_engine_anomaly(payload: EngineAnomalyTrainingRequest) -> dict[str, int | str]:
    try:
        sample_count = anomaly_service.train(payload.samples)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    return {"sample_count": sample_count, "model_version": anomaly_service.detector.VERSION}
