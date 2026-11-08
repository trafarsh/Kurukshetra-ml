"""Telemetry ingestion and retrieval endpoints."""
from typing import List, Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.models.telemetry import TelemetryRecord, TelemetryFile, Alert
from app.models.session import Session as KartSession
from app.schemas.telemetry import TelemetryIngestRequest, TelemetrySummaryResponse, TelemetryImportResponse
from app.telemetry.sd_importer import SDCardImporter

router = APIRouter(prefix="/telemetry", tags=["Telemetry"])
importer = SDCardImporter()


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


@router.post("/import", response_model=TelemetryImportResponse, status_code=status.HTTP_202_ACCEPTED)
async def import_sd_card_file(
    session_id: str = Form(...),
    file_format: str = Form("CSV"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Import raw MicroSD telemetry file (CSV or 16-byte binary), validate quality, and ingest."""
    session = db.query(KartSession).filter(KartSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Session '{session_id}' not found.")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty file uploaded.")

    # 1. Save immutable raw archive
    saved_path, sha256_hash = importer.save_raw_file(file.filename or "telemetry.csv", content)

    # 2. Parse and evaluate data quality
    if file_format.upper() == "CSV":
        decoded_text = content.decode("utf-8", errors="replace")
        records, quality_report = importer.parse_csv(decoded_text)
    else:
        binary_packets, quality_report = importer.parse_binary_stream(content)
        records = [
            {
                "timestamp_us": p.timestamp_ms * 1000,
                "speed_kmh": p.speed_kmh,
                "engine_rpm": p.engine_rpm,
                "engine_temp_c": p.engine_temp_c,
                "steering_angle_deg": p.steering_angle_deg,
                "throttle_percent": p.throttle_percent,
                "accel_x_g": p.accel_x_g,
                "accel_y_g": p.accel_y_g,
                "ttc_seconds": p.ttc_seconds,
                "warning_level": p.warning_level,
            }
            for p in binary_packets
        ]

    # 3. Store file record
    telemetry_file = TelemetryFile(
        session_id=session_id,
        file_name=file.filename or "unknown",
        file_path=saved_path,
        file_format=file_format.upper(),
        file_size_bytes=len(content),
        record_count=len(records),
        checksum_sha256=sha256_hash,
        is_processed=True,
    )
    db.add(telemetry_file)

    # 4. Bulk insert valid records
    db_records = [
        TelemetryRecord(
            session_id=session_id,
            timestamp_us=r["timestamp_us"],
            speed_kmh=r["speed_kmh"],
            engine_rpm=r["engine_rpm"],
            engine_temp_c=r["engine_temp_c"],
            steering_angle_deg=r["steering_angle_deg"],
            throttle_percent=r["throttle_percent"],
            accel_x_g=r["accel_x_g"],
            accel_y_g=r["accel_y_g"],
            ttc_seconds=r.get("ttc_seconds"),
            warning_level=r.get("warning_level", "SAFE"),
        )
        for r in records
    ]
    if db_records:
        db.bulk_save_objects(db_records)

    db.commit()

    return TelemetryImportResponse(
        file_id=telemetry_file.id,
        session_id=session_id,
        records_parsed=quality_report.valid_records,
        duration_seconds=quality_report.duration_seconds,
        data_quality={
            "total_records": quality_report.total_records,
            "valid_records": quality_report.valid_records,
            "rejected_records": quality_report.rejected_records,
            "duplicate_timestamps": quality_report.duplicate_timestamps,
            "clock_resets": quality_report.clock_resets,
            "missing_data_pct": quality_report.missing_data_pct,
            "checksum_sha256": quality_report.checksum_sha256,
            "anomalies": quality_report.anomalies,
        },
        laps_detected=0,
    )


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
