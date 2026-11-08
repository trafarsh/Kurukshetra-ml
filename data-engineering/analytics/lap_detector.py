"""
Lap Detection & Segmentation Engine.

Implements:
1. Dead-reckoning kinematic bicycle integration (Appendix D of Kurukshetra Kart Master Plan)
2. Cumulative track-distance lap boundary segmentation
3. Lap split metrics extraction (lap time, min/max speed, average RPM, peak lateral G)
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Optional
import numpy as np
import pandas as pd


@dataclass
class DetectedLap:
    lap_number: int
    start_index: int
    end_index: int
    start_timestamp_us: int
    end_timestamp_us: int
    lap_time_s: float
    max_speed_kmh: float
    min_speed_kmh: float
    avg_rpm: float
    max_lateral_g: float
    is_valid: bool


class DeadReckoner:
    """Kinematic bicycle model track distance and position estimator."""

    def __init__(self, wheelbase_m: float = 1.04, track_length_m: float = 850.0):
        self.wheelbase = wheelbase_m
        self.track_length = track_length_m
        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0  # Heading in radians
        self.lap_distance = 0.0
        self.lap_count = 0

    def update(self, wheel_speed_ms: float, steering_angle_rad: float, dt_s: float) -> tuple[float, int, float, float]:
        """Update position and lap progression."""
        v = wheel_speed_ms
        delta = max(-0.6, min(0.6, steering_angle_rad))  # Clamp physical steering rack limit ~35°

        # Kinematic bicycle equations
        self.theta += (v / self.wheelbase) * math.tan(delta) * dt_s
        self.x += v * math.cos(self.theta) * dt_s
        self.y += v * math.sin(self.theta) * dt_s
        self.lap_distance += v * dt_s

        crossed_line = False
        if self.lap_distance >= self.track_length:
            self.lap_distance -= self.track_length
            self.lap_count += 1
            crossed_line = True

        return self.lap_distance, self.lap_count, self.x, self.y


class LapDetector:
    def __init__(self, track_length_m: float = 850.0, wheelbase_m: float = 1.04):
        self.track_length_m = track_length_m
        self.wheelbase_m = wheelbase_m

    def detect_laps(self, df: pd.DataFrame) -> List[DetectedLap]:
        """Segment a continuous telemetry dataframe into discrete laps."""
        if len(df) < 50:
            return []

        dead_reckoner = DeadReckoner(wheelbase_m=self.wheelbase_m, track_length_m=self.track_length_m)
        laps: List[DetectedLap] = []

        lap_start_idx = 0
        current_lap = 1

        for i in range(1, len(df)):
            dt = (df.iloc[i]["timestamp_us"] - df.iloc[i - 1]["timestamp_us"]) / 1_000_000.0
            if dt <= 0 or dt > 0.5:
                dt = 0.05  # Default fallback 20Hz interval

            speed_ms = df.iloc[i]["speed_kmh"] / 3.6
            steering_rad = math.radians(df.iloc[i]["steering_angle_deg"])

            lap_dist, lap_count, _, _ = dead_reckoner.update(speed_ms, steering_rad, dt)

            if lap_count >= current_lap:
                # Segment lap
                lap_df = df.iloc[lap_start_idx:i]
                duration_s = (df.iloc[i]["timestamp_us"] - df.iloc[lap_start_idx]["timestamp_us"]) / 1_000_000.0

                # Validate lap (ignore pit lane rolls < 15 seconds or stop-stalls > 180 seconds)
                is_valid = 15.0 <= duration_s <= 180.0

                laps.append(
                    DetectedLap(
                        lap_number=current_lap,
                        start_index=lap_start_idx,
                        end_index=i,
                        start_timestamp_us=int(df.iloc[lap_start_idx]["timestamp_us"]),
                        end_timestamp_us=int(df.iloc[i]["timestamp_us"]),
                        lap_time_s=round(duration_s, 2),
                        max_speed_kmh=round(float(lap_df["speed_kmh"].max()), 1),
                        min_speed_kmh=round(float(lap_df["speed_kmh"].min()), 1),
                        avg_rpm=round(float(lap_df["engine_rpm"].mean()), 0),
                        max_lateral_g=round(float(lap_df["accel_y_g"].abs().max()), 2),
                        is_valid=is_valid,
                    )
                )

                lap_start_idx = i
                current_lap = lap_count + 1

        return laps

    def detect_gps_laps(
        self,
        df: pd.DataFrame,
        start_line_lat: float,
        start_line_lon: float,
        tolerance_m: float = 8.0,
    ) -> List[DetectedLap]:
        """Detect crossings of a GPS start line using latitude/longitude samples."""
        required = {"timestamp_us", "latitude", "longitude"}
        missing = required.difference(df.columns)
        if missing:
            raise ValueError(f"GPS telemetry is missing columns: {sorted(missing)}")
        if len(df) < 2:
            return []

        distances = self._haversine_m(df["latitude"], df["longitude"], start_line_lat, start_line_lon)
        crossings = [
            i for i in range(1, len(df))
            if distances.iloc[i] <= tolerance_m < distances.iloc[i - 1]
        ]
        return self._build_laps_from_boundaries(df, crossings)

    def detect_manual_laps(self, df: pd.DataFrame, marker_indices: List[int]) -> List[DetectedLap]:
        """Segment telemetry using explicit start-line sample indices."""
        if not marker_indices:
            return []
        boundaries = sorted(set(index for index in marker_indices if 0 <= index < len(df)))
        return self._build_laps_from_boundaries(df, boundaries)

    def _build_laps_from_boundaries(self, df: pd.DataFrame, boundaries: List[int]) -> List[DetectedLap]:
        laps: List[DetectedLap] = []
        for lap_number, (start, end) in enumerate(zip(boundaries, boundaries[1:]), 1):
            if end <= start:
                continue
            lap_df = df.iloc[start:end + 1]
            duration_s = (int(lap_df["timestamp_us"].iloc[-1]) - int(lap_df["timestamp_us"].iloc[0])) / 1e6
            laps.append(
                DetectedLap(
                    lap_number=lap_number,
                    start_index=start,
                    end_index=end,
                    start_timestamp_us=int(lap_df["timestamp_us"].iloc[0]),
                    end_timestamp_us=int(lap_df["timestamp_us"].iloc[-1]),
                    lap_time_s=round(duration_s, 2),
                    max_speed_kmh=round(float(lap_df["speed_kmh"].max()), 1) if "speed_kmh" in df else 0.0,
                    min_speed_kmh=round(float(lap_df["speed_kmh"].min()), 1) if "speed_kmh" in df else 0.0,
                    avg_rpm=round(float(lap_df["engine_rpm"].mean()), 0) if "engine_rpm" in df else 0.0,
                    max_lateral_g=round(float(lap_df["accel_y_g"].abs().max()), 2) if "accel_y_g" in df else 0.0,
                    is_valid=15.0 <= duration_s <= 180.0,
                )
            )
        return laps

    @staticmethod
    def _haversine_m(
        latitudes: pd.Series,
        longitudes: pd.Series,
        target_lat: float,
        target_lon: float,
    ) -> pd.Series:
        earth_radius_m = 6_371_000.0
        lat1 = np.radians(latitudes.to_numpy(dtype=float))
        lon1 = np.radians(longitudes.to_numpy(dtype=float))
        lat2 = math.radians(target_lat)
        lon2 = math.radians(target_lon)
        delta_lat = lat1 - lat2
        delta_lon = lon1 - lon2
        a = np.sin(delta_lat / 2) ** 2 + np.cos(lat1) * math.cos(lat2) * np.sin(delta_lon / 2) ** 2
        return pd.Series(2 * earth_radius_m * np.arcsin(np.sqrt(a)), index=latitudes.index)
