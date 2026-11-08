"""Session lifecycle management endpoints."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session as DBSession

from app.core.database import get_db
from app.models.session import Session, WeatherCondition, SetupConfiguration, Lap
from app.schemas.session import SessionCreate, SessionResponse
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/sessions", tags=["Sessions"])


@router.get("", response_model=List[SessionResponse])
def list_sessions(
    track_id: Optional[str] = Query(None),
    driver_id: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    db: DBSession = Depends(get_db),
):
    """Query telemetry sessions with optional filters."""
    query = db.query(Session)
    if track_id:
        query = query.filter(Session.track_id == track_id)
    if driver_id:
        query = query.filter(Session.driver_id == driver_id)
    if status_filter:
        query = query.filter(Session.status == status_filter)
    return query.order_by(Session.created_at.desc()).all()


@router.post("", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
def create_session(
    payload: SessionCreate,
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db),
):
    """Initiate a new active track session."""
    session = Session(
        name=payload.name,
        track_id=payload.track_id,
        driver_id=payload.driver_id,
        vehicle_id=payload.vehicle_id,
        vehicle_config_id=payload.vehicle_config_id,
        created_by=current_user.id,
        status="ACTIVE",
    )
    db.add(session)
    db.flush()

    if payload.weather:
        weather = WeatherCondition(
            session_id=session.id,
            ambient_temp_c=payload.weather.ambient_temp_c,
            track_temp_c=payload.weather.track_temp_c,
            relative_humidity_pct=payload.weather.relative_humidity_pct,
            barometric_pressure_hpa=payload.weather.barometric_pressure_hpa,
            air_density_kgm3=payload.weather.air_density_kgm3 or 1.18,
            track_condition=payload.weather.track_condition,
        )
        db.add(weather)

    if payload.setup:
        setup = SetupConfiguration(
            session_id=session.id,
            tire_pressure_front_psi=payload.setup.tire_pressure_front_psi,
            tire_pressure_rear_psi=payload.setup.tire_pressure_rear_psi,
            front_track_width_mm=payload.setup.front_track_width_mm,
            rear_track_width_mm=payload.setup.rear_track_width_mm,
            gear_sprocket_teeth=payload.setup.gear_sprocket_teeth,
            notes=payload.setup.notes,
        )
        db.add(setup)

    db.commit()
    db.refresh(session)
    return session


@router.get("/{session_id}", response_model=SessionResponse)
def get_session(session_id: str, db: DBSession = Depends(get_db)):
    """Retrieve session by ID with laps and weather metadata."""
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return session


@router.post("/{session_id}/finalize", response_model=SessionResponse)
def finalize_session(session_id: str, db: DBSession = Depends(get_db)):
    """Mark session as completed and aggregate best/average lap stats."""
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    laps = db.query(Lap).filter(Lap.session_id == session_id, Lap.is_valid == True).all()
    session.status = "COMPLETED"
    session.total_laps = len(laps)

    if laps:
        lap_times = [l.lap_time_s for l in laps]
        session.best_lap_time_s = min(lap_times)
        session.avg_lap_time_s = sum(lap_times) / len(lap_times)

    db.commit()
    db.refresh(session)
    return session

