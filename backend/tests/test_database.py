"""Test database schema creation and ORM operations."""
from app.models.user import Role, User
from app.models.vehicle import Vehicle, VehicleConfiguration
from app.models.driver import Driver
from app.models.track import Track, TrackSector
from app.core.security import hash_password


def test_create_and_query_role_and_user(db_session):
    role = Role(name="TEST_ENGINEER", description="Test role")
    db_session.add(role)
    db_session.flush()

    user = User(
        username="test_racer",
        email="test_racer@skcet.ac.in",
        hashed_password=hash_password("secretpass"),
        role_id=role.id,
    )
    db_session.add(user)
    db_session.commit()

    queried_user = db_session.query(User).filter(User.username == "test_racer").first()
    assert queried_user is not None
    assert queried_user.email == "test_racer@skcet.ac.in"
    assert queried_user.role.name == "TEST_ENGINEER"


def test_create_vehicle_with_configurations(db_session):
    vehicle = Vehicle(
        name="Kurukshetra IC-04 Test",
        chassis_code="TEST-CHASSIS-001",
        engine_type="125cc Honda GX390",
        dry_mass_kg=120.0,
        wheelbase_m=1.04,
        track_width_m=1.12,
    )
    db_session.add(vehicle)
    db_session.flush()

    config = VehicleConfiguration(
        vehicle_id=vehicle.id,
        name="Sprint High Downforce",
        drag_coefficient_cd=0.72,
        engine_power_kw=8.2,
    )
    db_session.add(config)
    db_session.commit()

    queried_v = db_session.query(Vehicle).filter(Vehicle.chassis_code == "TEST-CHASSIS-001").first()
    assert queried_v is not None
    assert len(queried_v.configurations) == 1
    assert queried_v.configurations[0].drag_coefficient_cd == 0.72


def test_create_track_with_sectors(db_session):
    track = Track(
        name="SKCET Test Oval",
        length_meters=600.0,
        num_turns=4,
        surface_type="ASPHALT",
    )
    db_session.add(track)
    db_session.flush()

    s1 = TrackSector(track_id=track.id, sector_number=1, start_distance_m=0, end_distance_m=200, is_corner=False)
    s2 = TrackSector(track_id=track.id, sector_number=2, start_distance_m=200, end_distance_m=400, is_corner=True, corner_radius_m=22.0)
    db_session.add_all([s1, s2])
    db_session.commit()

    queried_track = db_session.query(Track).filter(Track.name == "SKCET Test Oval").first()
    assert queried_track is not None
    assert len(queried_track.sectors) == 2

