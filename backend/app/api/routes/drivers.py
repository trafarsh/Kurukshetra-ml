"""Driver profile management endpoints."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.driver import Driver
from app.schemas.driver import DriverCreate, DriverResponse

router = APIRouter(prefix="/drivers", tags=["Drivers"])


@router.get("", response_model=List[DriverResponse])
def list_drivers(db: Session = Depends(get_db)):
    """List all registered drivers."""
    return db.query(Driver).all()


@router.post("", response_model=DriverResponse, status_code=status.HTTP_201_CREATED)
def create_driver(payload: DriverCreate, db: Session = Depends(get_db)):
    """Register a new driver."""
    driver = Driver(
        name=payload.name,
        racing_number=payload.racing_number,
        weight_kg=payload.weight_kg,
        experience_level=payload.experience_level,
    )
    db.add(driver)
    db.commit()
    db.refresh(driver)
    return driver


@router.get("/{driver_id}", response_model=DriverResponse)
def get_driver(driver_id: str, db: Session = Depends(get_db)):
    """Get driver details by ID."""
    driver = db.query(Driver).filter(Driver.id == driver_id).first()
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Driver '{driver_id}' not found.",
        )
    return driver

