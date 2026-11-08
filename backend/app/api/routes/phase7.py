"""Phase 7 recommendations, report exports, and session replay endpoints."""
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from app.core.config import settings
from app.services.phase7 import RecommendationEngine, ReportExporter, SessionReplay

router = APIRouter(tags=["Phase 7 Analytics"])
recommendation_engine = RecommendationEngine()
report_exporter = ReportExporter(settings.REPORTS_STORAGE_DIR)
session_replay = SessionReplay()


class RecommendationRequest(BaseModel):
    metrics: dict[str, float]


class ReportRequest(BaseModel):
    report_id: str = Field(min_length=1, max_length=150)
    report_type: str = Field(default="SESSION_DEBRIEF", min_length=1, max_length=50)
    telemetry: list[dict[str, Any]] = Field(default_factory=list)
    summary: dict[str, Any] = Field(default_factory=dict)


class ReplayRequest(BaseModel):
    records: list[dict[str, Any]]
    speed: float = Field(default=1.0, gt=0)


@router.post("/recommendations")
def create_recommendations(payload: RecommendationRequest) -> dict[str, Any]:
    try:
        recommendations = recommendation_engine.recommend(payload.metrics)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    return {"recommendations": [recommendation.__dict__ for recommendation in recommendations]}


@router.post("/reports", status_code=status.HTTP_201_CREATED)
def create_report(payload: ReportRequest) -> dict[str, str]:
    try:
        return report_exporter.generate(payload.report_id, payload.telemetry, payload.summary, payload.report_type)
    except (OSError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc


@router.get("/reports/{report_id}/{file_format}")
def download_report(report_id: str, file_format: str) -> FileResponse:
    if file_format not in {"pdf", "csv"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="file_format must be pdf or csv")
    path = Path(settings.REPORTS_STORAGE_DIR) / f"{ReportExporter._safe_id(report_id)}.{file_format}"
    if not path.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report file not found")
    return FileResponse(path, filename=path.name)


@router.post("/replay/prepare")
def prepare_replay(payload: ReplayRequest) -> dict[str, Any]:
    try:
        frames = session_replay.prepare(payload.records, payload.speed)
    except (KeyError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    return {"frame_count": len(frames), "frames": frames}
