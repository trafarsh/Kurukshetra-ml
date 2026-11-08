"""Telemetry ingestion and retrieval endpoints."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.models.telemetry import TelemetryRecord, Alert
from app.models.session import Session as KartSession
from app.schemas.telemetry import TelemetryIngestRequest, TelemetrySummaryResponse

router = APIRouter(prefix="/telemetry", tags=["Telemetry"])


@router.post("/ingest", status_code=status.HTTP_200_OK)
def ingest_telemetry_packet(packet: TelemetryIngestRequest, db: Session = Depends(get_db)):
    """Ingest a single live telemetry packet into time-series store."""
    record = TelemetryRecord(
        session_id=packet.session_id,
        timestamp_us=packet.timestamp_us,
        speed_kmh=packet.speed_kmh,
        engine_rpm=packet.engine_rpm,
        engine_temp_c=packet.engine_temp_c,
        steering_angle_deg=packet.steering_angle_deg,
        throttle_percent=packet.throttle_percent,
        accel_x_g=packet.accel_x_g,
        accel_y_g=packet.accel_y_g,
        accel_z_g=packet.accel_z_g,
        gyro_z_degps=packet.gyro_z_degps,
        obstacle_distance_cm=packet.obstacle_distance_cm,
        closing_speed_mps=packet.closing_speed_mps,
        ttc_seconds=packet.ttc_seconds,
        warning_level=packet.warning_level,
        sensor_status=packet.sensor_status,
    )
    db.add(record)

    # Automatically create alert if danger state detected
    if packet.warning_level == "DANGER" and packet.ttc_seconds is not None:
        alert = Alert(
            session_id=packet.session_id,
            timestamp_us=packet.timestamp_us,
            alert_type="TTC_DANGER",
            severity="CRITICAL",
            message=f"Collision hazard: TTC = {packet.ttc_seconds:.2f}s, closing speed = {packet.closing_speed_mps:.1f} m/s",
        )
        db.add(alert)

    db.commit()
    return {"status": "ACCEPTED", "timestamp_us": packet.timestamp_us}


@router.get("/{session_id}")
def get_session_telemetry(
    session_id: str,
    limit: int = Query(500, le=5000),
    downsample: int = Query(1, ge=1),
    db: Session = Depends(get_db),
):
    """Retrieve telemetry traces for visualization, with optional downsampling."""
    records = (
        db.query(TelemetryRecord)
        .filter(TelemetryRecord.session_id == session_id)
        .order_by(TelemetryRecord.timestamp_us.asc())
        .limit(limit * downsample)
        .all()
    )
    # Downsample if requested
    if downsample > 1:
        records = records[::downsample]

    return [
        {
            "timestamp_us": r.timestamp_us,
            "speed_kmh": r.speed_kmh,
            "engine_rpm": r.engine_rpm,
            "engine_temp_c": r.engine_temp_c,
            "steering_angle_deg": r.steering_angle_deg,
            "throttle_percent": r.throttle_percent,
            "accel_x_g": r.accel_x_g,
            "accel_y_g": r.accel_y_g,
            "ttc_seconds": r.ttc_seconds,
            "warning_level": r.warning_level,
        }
        for r in records
    ]


@router.get("/{session_id}/summary", response_model=TelemetrySummaryResponse)
def get_telemetry_summary(session_id: str, db: Session = Depends(get_db)):
    """Compute aggregate statistical summary of a session's telemetry."""
    stats = (
        db.query(
            func.count(TelemetryRecord.id).label("count"),
            func.max(TelemetryRecord.speed_kmh).label("max_speed"),
            func.avg(TelemetryRecord.speed_kmh).label("avg_speed"),
            func.max(TelemetryRecord.engine_rpm).label("max_rpm"),
            func.max(TelemetryRecord.engine_temp_c).label("max_temp"),
            func.max(func.abs(TelemetryRecord.accel_y_g)).label("max_lat_g"),
        )
        .filter(TelemetryRecord.session_id == session_id)
        .first()
    )

    warnings_count = (
        db.query(func.count(Alert.id))
        .filter(Alert.session_id == session_id, Alert.severity == "CRITICAL")
        .scalar()
        or 0
    )

    if not stats or not stats.count:
        return TelemetrySummaryResponse(
            session_id=session_id,
            record_count=0,
            max_speed_kmh=0.0,
            avg_speed_kmh=0.0,
            max_rpm=0,
            max_temp_c=0.0,
            max_lateral_g=0.0,
            active_warnings_count=0,
        )

    return TelemetrySummaryResponse(
        session_id=session_id,
        record_count=stats.count or 0,
        max_speed_kmh=float(stats.max_speed or 0.0),
        avg_speed_kmh=float(stats.avg_speed or 0.0),
        max_rpm=int(stats.max_rpm or 0),
        max_temp_c=float(stats.max_temp or 0.0),
        max_lateral_g=float(stats.max_lat_g or 0.0),
        active_warnings_count=warnings_count,
    )

