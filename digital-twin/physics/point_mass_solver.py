"""
Point-Mass Vehicle Dynamics Physics Solver.

Governing Physics Equations:
1. Lateral Grip Limit:
     a_lat_max = mu * g
     v_corner_max = sqrt(mu * g * R)

2. Aerodynamic Drag:
     F_drag = 0.5 * rho * Cd * A * v^2

3. Rolling Resistance:
     F_rolling = Crr * mass * g

4. Power-Limited Acceleration:
     a_power = (P_engine / v - F_drag - F_rolling) / mass

5. Low-Speed Asymptotic Stabilization:
     As v -> 0, traction limit applies: a_tractive_max = mu * g.
     Prevents division-by-zero singularity.

6. Braking Limit:
     a_braking_max = -0.85 * mu * g
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Optional, Tuple
import numpy as np


@dataclass
class TrackSegment:
    segment_id: int
    length_m: float
    is_corner: bool
    corner_radius_m: Optional[float] = None  # None for straights


@dataclass
class SimulationPoint:
    distance_m: float
    speed_kmh: float
    accel_x_g: float
    accel_y_g: float
    limiting_factor: str  # POWER, GRIP, BRAKING, TRACTION


@dataclass
class SimulationOutput:
    lap_time_s: float
    top_speed_kmh: float
    avg_speed_kmh: float
    points: List[SimulationPoint]


class PointMassSolver:
    def __init__(
        self,
        mass_kg: float = 183.0,          # Kart 115kg + Driver 68kg
        effective_grip_mu: float = 1.15,
        drag_cd: float = 0.65,
        frontal_area_m2: float = 0.42,
        rolling_resistance_crr: float = 0.018,
        engine_power_kw: float = 7.5,
        air_density_kgm3: float = 1.18,
        gravity_mps2: float = 9.81,
    ):
        self.mass = mass_kg
        self.mu = effective_grip_mu
        self.cd = drag_cd
        self.area = frontal_area_m2
        self.crr = rolling_resistance_crr
        self.power_watts = engine_power_kw * 1000.0
        self.rho = air_density_kgm3
        self.g = gravity_mps2

    def calculate_corner_speed(self, radius_m: float) -> float:
        """Calculate max apex cornering speed: v = sqrt(mu * g * R) in m/s."""
        return math.sqrt(self.mu * self.g * radius_m)

    def calculate_longitudinal_accel(self, speed_ms: float) -> Tuple[float, str]:
        """
        Calculate forward acceleration in m/s² respecting drag, rolling resistance,
        power curve, and traction limits at low speeds.
        """
        v_safe = max(speed_ms, 2.5)  # Transition at 2.5 m/s (~9 km/h)

        f_drag = 0.5 * self.rho * self.cd * self.area * (v_safe ** 2)
        f_rolling = self.crr * self.mass * self.g

        # Engine tractive force
        f_engine = self.power_watts / v_safe
        net_force = f_engine - f_drag - f_rolling

        accel = net_force / self.mass

        # Clamp by tire longitudinal traction limit: a_max = mu * g
        max_tractive_accel = self.mu * self.g * 0.90
        if accel > max_tractive_accel:
            return max_tractive_accel, "TRACTION"

        return max(0.0, accel), "POWER"

    def simulate_track(self, segments: List[TrackSegment], ds_m: float = 2.0) -> SimulationOutput:
        """
        Discretise track into increments ds_m and solve the forward-backward
        velocity envelope along the circuit profile.
        """
        profile_dist = []
        corner_speed_limits = []

        total_dist = 0.0
        for seg in segments:
            steps = max(1, int(round(seg.length_m / ds_m)))
            step_len = seg.length_m / steps
            for _ in range(steps):
                profile_dist.append(total_dist)
                if seg.is_corner and seg.corner_radius_m and seg.corner_radius_m > 0:
                    v_limit = self.calculate_corner_speed(seg.corner_radius_m)
                else:
                    v_limit = 35.0  # Max physical gear/aero limit ~126 km/h
                corner_speed_limits.append(v_limit)
                total_dist += step_len

        n = len(profile_dist)

        # 2. Forward pass starting from corner exit / launch speed
        # If last segment is a corner, start at that corner apex speed; otherwise start at 10 m/s
        v_start = min(corner_speed_limits[-1], 12.0)
        forward_speeds = np.zeros(n)
        forward_speeds[0] = v_start
        limiting_factors = ["POWER"] * n

        v = v_start
        for i in range(1, n):
            dx = profile_dist[i] - profile_dist[i - 1]
            a, factor = self.calculate_longitudinal_accel(v)
            v_next = math.sqrt(v ** 2 + 2 * a * dx)
            if v_next > corner_speed_limits[i]:
                v_next = corner_speed_limits[i]
                limiting_factors[i] = "GRIP"
            else:
                limiting_factors[i] = factor
            forward_speeds[i] = v_next
            v = v_next

        # 3. Backward pass: braking into corners
        backward_speeds = np.zeros(n)
        backward_speeds[-1] = forward_speeds[-1]
        a_brake = self.mu * self.g * 0.85

        for i in range(n - 2, -1, -1):
            dx = profile_dist[i + 1] - profile_dist[i]
            v_allowed = math.sqrt(backward_speeds[i + 1] ** 2 + 2 * a_brake * dx)
            if v_allowed < forward_speeds[i]:
                backward_speeds[i] = v_allowed
                limiting_factors[i] = "BRAKING"
            else:
                backward_speeds[i] = forward_speeds[i]

        # 4. Integrate total lap time and compile simulation points
        sim_points: List[SimulationPoint] = []
        total_time_s = 0.0

        for i in range(n):
            v_ms = backward_speeds[i]
            dx = ds_m if i == 0 else profile_dist[i] - profile_dist[i - 1]
            dt = dx / max(v_ms, 1.0)
            total_time_s += dt

            if i < n - 1:
                ax = (backward_speeds[i + 1] - backward_speeds[i]) / dt / self.g
            else:
                ax = 0.0

            if corner_speed_limits[i] < 30.0:
                ay = min(self.mu, (v_ms ** 2) / (corner_speed_limits[i] ** 2 / (self.mu * self.g)) / self.g)
            else:
                ay = 0.0

            sim_points.append(
                SimulationPoint(
                    distance_m=round(profile_dist[i], 1),
                    speed_kmh=round(v_ms * 3.6, 1),
                    accel_x_g=round(ax, 2),
                    accel_y_g=round(ay, 2),
                    limiting_factor=limiting_factors[i],
                )
            )

        speed_kmh_arr = backward_speeds * 3.6

        return SimulationOutput(
            lap_time_s=round(total_time_s, 2),
            top_speed_kmh=round(float(speed_kmh_arr.max()), 1),
            avg_speed_kmh=round(float(speed_kmh_arr.mean()), 1),
            points=sim_points,
        )
