"""Machine-learning inference endpoints."""
from typing import List

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.services.anomaly_detector import anomaly_service
from app.services.phase5_models import phase5_service

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


class FeatureRequest(BaseModel):
    features: List[float]


class GripRequest(BaseModel):
    lateral_g: float = Field(ge=0)
    speed_kmh: float | None = Field(default=None, ge=0)
    radius_m: float | None = Field(default=None, gt=0)
    sensor_quality: float = Field(default=1.0, gt=0, le=1)


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


@router.post("/lap-time/predict")
def predict_lap_time(payload: FeatureRequest) -> dict[str, float | str]:
    try:
        result = phase5_service.predict_lap_time(payload.features)
    except (RuntimeError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    return {"lap_time_s": result.lap_time_s, "model_version": result.model_version}


@router.post("/driver-behaviour/predict")
def predict_driver_behaviour(payload: FeatureRequest) -> dict[str, float | str]:
    try:
        result = phase5_service.predict_behaviour(payload.features)
    except (RuntimeError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    return {
        "behaviour": result.behaviour,
        "confidence": result.confidence,
        "model_version": result.model_version,
    }


@router.post("/grip/estimate")
def estimate_dynamic_grip(payload: GripRequest) -> dict[str, float | str | None]:
    result = phase5_service.estimate_grip(
        payload.lateral_g,
        payload.speed_kmh,
        payload.radius_m,
        payload.sensor_quality,
    )
    return {
        "effective_mu": result.effective_mu,
        "measured_mu": result.measured_mu,
        "theoretical_mu": result.theoretical_mu,
        "confidence": result.confidence,
        "model_version": result.model_version,
    }
