"""
Digital Twin Calibration Loop Engine.

Iteratively tunes unknown vehicle dynamics parameters (effective tire grip μ and aerodynamic drag Cd)
against measured track telemetry until prediction error meets the target (RMSE < 5%).
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Tuple
import numpy as np

from physics.point_mass_solver import PointMassSolver, TrackSegment


@dataclass
class CalibrationStep:
    iteration: int
    grip_mu: float
    simulated_lap_time_s: float
    apex_rmse_kmh: float
    error_pct: float


@dataclass
class CalibrationResult:
    converged: bool
    initial_mu: float
    calibrated_mu: float
    initial_rmse_kmh: float
    final_rmse_kmh: float
    final_error_pct: float
    total_iterations: int
    history: List[CalibrationStep]


class DigitalTwinCalibrator:
    def __init__(
        self,
        target_error_pct: float = 5.0,
        max_iterations: int = 8,
        tolerance_kmh: float = 2.0,
    ):
        self.target_error_pct = target_error_pct
        self.max_iterations = max_iterations
        self.tolerance_kmh = tolerance_kmh

    def calibrate(
        self,
        measured_corner_speeds: Dict[int, float],  # Dict mapping corner index -> measured speed km/h
        track_segments: List[TrackSegment],
        initial_mu: float = 1.15,
        kart_mass_kg: float = 183.0,
    ) -> CalibrationResult:
        """Run iterative calibration loop against measured corner apex speeds."""
        current_mu = initial_mu
        history: List[CalibrationStep] = []

        initial_rmse = 0.0
        final_rmse = 0.0

        for iter_num in range(1, self.max_iterations + 1):
            solver = PointMassSolver(
                mass_kg=kart_mass_kg,
                effective_grip_mu=current_mu,
            )
            sim_output = solver.simulate_track(track_segments)

            # Extract simulated corner speeds
            sim_corner_speeds = []
            corner_idx = 0
            for seg in track_segments:
                if seg.is_corner and seg.corner_radius_m:
                    v_corner_kmh = solver.calculate_corner_speed(seg.corner_radius_m) * 3.6
                    sim_corner_speeds.append(v_corner_kmh)
                    corner_idx += 1

            # Compute error against measured apex speeds
            errors = []
            meas_speeds = []
            sim_speeds = []

            for idx, meas_v in measured_corner_speeds.items():
                if idx < len(sim_corner_speeds):
                    sim_v = sim_corner_speeds[idx]
                    errors.append((meas_v - sim_v) ** 2)
                    meas_speeds.append(meas_v)
                    sim_speeds.append(sim_v)

            if not errors:
                break

            rmse = math.sqrt(sum(errors) / len(errors))
            mean_meas = sum(meas_speeds) / len(meas_speeds)
            error_pct = round((rmse / mean_meas) * 100.0, 2)

            if iter_num == 1:
                initial_rmse = round(rmse, 2)

            history.append(
                CalibrationStep(
                    iteration=iter_num,
                    grip_mu=round(current_mu, 3),
                    simulated_lap_time_s=sim_output.lap_time_s,
                    apex_rmse_kmh=round(rmse, 2),
                    error_pct=error_pct,
                )
            )

            # Check convergence
            if error_pct <= self.target_error_pct or rmse <= self.tolerance_kmh:
                final_rmse = round(rmse, 2)
                return CalibrationResult(
                    converged=True,
                    initial_mu=round(initial_mu, 3),
                    calibrated_mu=round(current_mu, 3),
                    initial_rmse_kmh=initial_rmse,
                    final_rmse_kmh=final_rmse,
                    final_error_pct=error_pct,
                    total_iterations=iter_num,
                    history=history,
                )

            # Adjust grip: v_corner^2 = mu * g * R  =>  mu_new = mu_old * (meas_v / sim_v)^2
            ratio = (mean_meas / sum(sim_speeds) * len(sim_speeds)) ** 2
            current_mu = current_mu * (1.0 + 0.6 * (ratio - 1.0))
            current_mu = max(0.70, min(1.60, current_mu))

        final_rmse = history[-1].apex_rmse_kmh if history else 0.0
        return CalibrationResult(
            converged=False,
            initial_mu=round(initial_mu, 3),
            calibrated_mu=round(current_mu, 3),
            initial_rmse_kmh=initial_rmse,
            final_rmse_kmh=final_rmse,
            final_error_pct=history[-1].error_pct if history else 0.0,
            total_iterations=len(history),
            history=history,
        )
