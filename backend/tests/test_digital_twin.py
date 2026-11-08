"""Unit tests for Phase 6 Digital Twin Physics Engine and Calibration."""
import pytest
from physics.point_mass_solver import PointMassSolver, TrackSegment
from calibration.calibration_loop import DigitalTwinCalibrator
from scenarios.what_if_engine import WhatIfEngine


def test_point_mass_governing_equations():
    """Verify physical equations for corner speed, drag, and low-speed stability."""
    solver = PointMassSolver(
        mass_kg=183.0,
        effective_grip_mu=1.20,
        engine_power_kw=7.5,
    )

    # 1. Corner speed formula: v = sqrt(mu * g * R)
    # For R = 20m, mu = 1.20, g = 9.81: v = sqrt(1.20 * 9.81 * 20) = sqrt(235.44) ~ 15.344 m/s = 55.24 km/h
    corner_v_ms = solver.calculate_corner_speed(20.0)
    assert abs(corner_v_ms * 3.6 - 55.24) < 0.1

    # 2. Low-speed stability: zero division prevented when v -> 0
    accel_zero_speed, factor = solver.calculate_longitudinal_accel(0.0)
    assert accel_zero_speed > 0.0
    assert factor == "TRACTION"

    # 3. High-speed power-limited acceleration: P/v decreases as speed increases
    accel_low, _ = solver.calculate_longitudinal_accel(5.0)
    accel_high, _ = solver.calculate_longitudinal_accel(20.0)
    assert accel_low > accel_high


def test_track_simulation_envelope():
    """Simulate a representative 850m track and check for reasonable lap time."""
    segments = [
        TrackSegment(segment_id=1, length_m=280.0, is_corner=False),
        TrackSegment(segment_id=2, length_m=90.0, is_corner=True, corner_radius_m=18.5),
        TrackSegment(segment_id=3, length_m=220.0, is_corner=False),
        TrackSegment(segment_id=4, length_m=120.0, is_corner=True, corner_radius_m=28.0),
        TrackSegment(segment_id=5, length_m=140.0, is_corner=False),
    ]

    solver = PointMassSolver(effective_grip_mu=1.20)
    output = solver.simulate_track(segments)

    assert 35.0 <= output.lap_time_s <= 55.0
    assert output.top_speed_kmh > 70.0
    assert len(output.points) > 0


def test_calibration_loop_convergence():
    """Verify that calibration tunes effective grip mu to bring RMSE under 5%."""
    segments = [
        TrackSegment(segment_id=1, length_m=300.0, is_corner=False),
        TrackSegment(segment_id=2, length_m=100.0, is_corner=True, corner_radius_m=20.0),
        TrackSegment(segment_id=3, length_m=300.0, is_corner=False),
        TrackSegment(segment_id=4, length_m=100.0, is_corner=True, corner_radius_m=25.0),
    ]

    measured_corners = {0: 56.5, 1: 63.2}

    calibrator = DigitalTwinCalibrator(target_error_pct=5.0, max_iterations=6)
    result = calibrator.calibrate(
        measured_corner_speeds=measured_corners,
        track_segments=segments,
        initial_mu=1.00,
    )

    assert result.converged is True
    assert result.final_error_pct <= 5.0
    assert result.calibrated_mu > 1.00


def test_what_if_scenario_deltas():
    """Verify that What-If scenarios correctly quantify lap time deltas without changing baseline."""
    segments = [
        TrackSegment(segment_id=1, length_m=400.0, is_corner=False),
        TrackSegment(segment_id=2, length_m=100.0, is_corner=True, corner_radius_m=22.0),
    ]

    baseline_solver = PointMassSolver(mass_kg=183.0, effective_grip_mu=1.15)
    engine = WhatIfEngine(segments)

    delta, _ = engine.run_scenario(
        scenario_name="Ballast +15kg",
        baseline_solver=baseline_solver,
        delta_mass_kg=15.0,
    )

    assert delta.delta_lap_time_s > 0.0
    assert delta.simulated_mass_kg == 198.0
    assert delta.is_simulated is True
