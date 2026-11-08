"""Test vehicle API routes."""

def test_create_and_list_vehicles(client):
    new_vehicle = {
        "name": "Kurukshetra IC-04 Sprint",
        "chassis_code": "SKCET-2026-SP1",
        "engine_type": "125cc 4-Stroke IC Engine",
        "dry_mass_kg": 115.0,
        "wheelbase_m": 1.04,
        "track_width_m": 1.12,
        "configurations": [
            {
                "name": "Standard Gearing",
                "drag_coefficient_cd": 0.65,
                "frontal_area_m2": 0.42,
                "rolling_resistance_crr": 0.018,
                "engine_power_kw": 7.5,
                "max_rpm": 9500,
                "gear_ratio": 4.2,
            }
        ],
    }

    create_res = client.post("/api/v1/vehicles", json=new_vehicle)
    assert create_res.status_code == 201
    created_data = create_res.json()
    assert created_data["chassis_code"] == "SKCET-2026-SP1"
    vehicle_id = created_data["id"]

    # List vehicles
    list_res = client.get("/api/v1/vehicles")
    assert list_res.status_code == 200
    vehicles = list_res.json()
    assert any(v["id"] == vehicle_id for v in vehicles)

    # Get single vehicle
    get_res = client.get(f"/api/v1/vehicles/{vehicle_id}")
    assert get_res.status_code == 200
    assert get_res.json()["name"] == "Kurukshetra IC-04 Sprint"

