"""Track and sector management endpoints."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.track import Track, TrackSector
from app.schemas.track import TrackCreate, TrackResponse

router = APIRouter(prefix="/tracks", tags=["Tracks"])


@router.get("", response_model=List[TrackResponse])
def list_tracks(db: Session = Depends(get_db)):
    """List all registered circuits and test tracks."""
    return db.query(Track).all()


@router.post("", response_model=TrackResponse, status_code=status.HTTP_201_CREATED)
def create_track(payload: TrackCreate, db: Session = Depends(get_db)):
    """Register a new track layout with sector definitions."""
    track = Track(
        name=payload.name,
        location=payload.location,
        length_meters=payload.length_meters,
        num_turns=payload.num_turns,
        surface_type=payload.surface_type,
        centerline_geometry=payload.centerline_geometry,
    )
    db.add(track)
    db.flush()

    if payload.sectors:
        for s in payload.sectors:
            sector = TrackSector(
                track_id=track.id,
                sector_number=s.sector_number,
                start_distance_m=s.start_distance_m,
                end_distance_m=s.end_distance_m,
                is_corner=s.is_corner,
                corner_radius_m=s.corner_radius_m,
                corner_direction=s.corner_direction,
            )
            db.add(sector)
    else:
        # Generate default 3-sector division
        third = payload.length_meters / 3.0
        for i in range(1, 4):
            db.add(
                TrackSector(
                    track_id=track.id,
                    sector_number=i,
                    start_distance_m=(i - 1) * third,
                    end_distance_m=i * third,
                    is_corner=(i == 2),
                )
            )

    db.commit()
    db.refresh(track)
    return track


@router.get("/{track_id}", response_model=TrackResponse)
def get_track(track_id: str, db: Session = Depends(get_db)):
    """Retrieve full track layout by ID."""
    track = db.query(Track).filter(Track.id == track_id).first()
    if not track:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Track not found")
    return track

