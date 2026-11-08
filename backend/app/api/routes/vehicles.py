"""Vehicle and vehicle configuration management endpoints."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.vehicle import Vehicle, VehicleConfiguration
from app.schemas.vehicle import VehicleCreate, VehicleResponse, VehicleUpdate, VehicleConfigCreate, VehicleConfigResponse

router = APIRouter(prefix="/vehicles", tags=["Vehicles"])


@router.get("", response_model=List[VehicleResponse])
def list_vehicles(db: Session = Depends(get_db)):
    """List all registered vehicles with their configurations."""
    return db.query(Vehicle).all()


@router.post("", response_model=VehicleResponse, status_code=status.HTTP_201_CREATED)
def create_vehicle(payload: VehicleCreate, db: Session = Depends(get_db)):
    """Register a new vehicle with optional initial configurations."""
    existing = db.query(Vehicle).filter(Vehicle.chassis_code == payload.chassis_code).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Vehicle with chassis code '{payload.chassis_code}' already registered.",
        )

    vehicle = Vehicle(
        name=payload.name,
        chassis_code=payload.chassis_code,
        engine_type=payload.engine_type,
        dry_mass_kg=payload.dry_mass_kg,
        wheelbase_m=payload.wheelbase_m,
        track_width_m=payload.track_width_m,
    )
    db.add(vehicle)
    db.flush()

    # Create default configuration if provided
    if payload.configurations:
        for cfg in payload.configurations:
            config = VehicleConfiguration(
                vehicle_id=vehicle.id,
                name=cfg.name,
                drag_coefficient_cd=cfg.drag_coefficient_cd,
                frontal_area_m2=cfg.frontal_area_m2,
                rolling_resistance_crr=cfg.rolling_resistance_crr,
                engine_power_kw=cfg.engine_power_kw,
                max_rpm=cfg.max_rpm,
                gear_ratio=cfg.gear_ratio,
            )
            db.add(config)
    else:
        # Create baseline V1 trim
        default_cfg = VehicleConfiguration(
            vehicle_id=vehicle.id,
            name="V1 Baseline Trim",
        )
        db.add(default_cfg)

    db.commit()
    db.refresh(vehicle)
    return vehicle


@router.get("/{vehicle_id}", response_model=VehicleResponse)
def get_vehicle(vehicle_id: str, db: Session = Depends(get_db)):
    """Retrieve vehicle details by ID."""
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vehicle '{vehicle_id}' not found.",
        )
    return vehicle


@router.put("/{vehicle_id}", response_model=VehicleResponse)
def update_vehicle(vehicle_id: str, payload: VehicleUpdate, db: Session = Depends(get_db)):
    """Update physical specifications of a vehicle."""
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(vehicle, field, value)

    db.commit()
    db.refresh(vehicle)
    return vehicle

