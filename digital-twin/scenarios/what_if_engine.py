"""
What-If Scenario Simulation Engine.

Enables engineers to explore hypothetical kart setup changes:
- Vehicle mass variations (lightening or ballast)
- Tire compound / grip variations (wet weather or high-grip compound)
- Engine tuning (power changes, carburetor re-jetting)
- Aerodynamic drag changes (front fairing, airbox)

Strict Discipline: All scenario results are tagged as virtual predictions and never
masquerade as measured physical telemetry.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional
from physics.point_mass_solver import PointMassSolver, TrackSegment, SimulationOutput


@dataclass
class ScenarioDelta:
    scenario_name: str
    baseline_lap_time_s: float
    simulated_lap_time_s: float
    delta_lap_time_s: float
    baseline_top_speed_kmh: float
    simulated_top_speed_kmh: float
    delta_top_speed_kmh: float
    simulated_mass_kg: float
    simulated_grip_mu: float
    is_simulated: bool = True


class WhatIfEngine:
    def __init__(self, track_segments: List[TrackSegment]):
        self.track_segments = track_segments

    def run_scenario(
        self,
        scenario_name: str,
        baseline_solver: PointMassSolver,
        delta_mass_kg: float = 0.0,
        delta_grip_mu: float = 0.0,
        delta_power_kw: float = 0.0,
        delta_cd: float = 0.0,
    ) -> tuple[ScenarioDelta, SimulationOutput]:
        """Execute a comparative simulation against a calibrated baseline configuration."""
        baseline_out = baseline_solver.simulate_track(self.track_segments)

        new_mass = max(100.0, baseline_solver.mass + delta_mass_kg)
        new_mu = max(0.50, min(1.80, baseline_solver.mu + delta_grip_mu))
        new_power_kw = max(2.0, (baseline_solver.power_watts / 1000.0) + delta_power_kw)
        new_cd = max(0.20, baseline_solver.cd + delta_cd)

        scenario_solver = PointMassSolver(
            mass_kg=new_mass,
            effective_grip_mu=new_mu,
            engine_power_kw=new_power_kw,
            drag_cd=new_cd,
            frontal_area_m2=baseline_solver.area,
            rolling_resistance_crr=baseline_solver.crr,
            air_density_kgm3=baseline_solver.rho,
            gravity_mps2=baseline_solver.g,
        )

        scenario_out = scenario_solver.simulate_track(self.track_segments)

        delta_t = round(scenario_out.lap_time_s - baseline_out.lap_time_s, 2)
        delta_v = round(scenario_out.top_speed_kmh - baseline_out.top_speed_kmh, 1)

        delta = ScenarioDelta(
            scenario_name=scenario_name,
            baseline_lap_time_s=baseline_out.lap_time_s,
            simulated_lap_time_s=scenario_out.lap_time_s,
            delta_lap_time_s=delta_t,
            baseline_top_speed_kmh=baseline_out.top_speed_kmh,
            simulated_top_speed_kmh=scenario_out.top_speed_kmh,
            delta_top_speed_kmh=delta_v,
            simulated_mass_kg=new_mass,
            simulated_grip_mu=new_mu,
            is_simulated=True,
        )

        return delta, scenario_out
