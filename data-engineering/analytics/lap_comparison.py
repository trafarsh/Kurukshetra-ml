"""Multi-lap trace comparison and delta metrics."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class LapDelta:
    reference_lap: int
    comparison_lap: int
    delta_time_s: float
    mean_delta_speed_kmh: float
    max_delta_speed_kmh: float
    distance_fraction: list[float]
    delta_speed_kmh: list[float]


class LapComparison:
    """Compare laps on a normalized distance axis."""

    def __init__(self, points: int = 200):
        if points < 2:
            raise ValueError("points must be at least 2")
        self.points = points

    def compare(
        self,
        reference_df: pd.DataFrame,
        comparison_df: pd.DataFrame,
        reference_lap: int = 1,
        comparison_lap: int = 2,
    ) -> LapDelta:
        for frame in (reference_df, comparison_df):
            missing = {"timestamp_us", "speed_kmh"}.difference(frame.columns)
            if missing:
                raise ValueError(f"Lap data is missing columns: {sorted(missing)}")
            if len(frame) < 2:
                raise ValueError("Each lap must contain at least two records")

        axis = np.linspace(0.0, 1.0, self.points)
        ref_speed = self._resample(reference_df, axis)
        cmp_speed = self._resample(comparison_df, axis)
        ref_time = float(reference_df["timestamp_us"].iloc[-1] - reference_df["timestamp_us"].iloc[0]) / 1e6
        cmp_time = float(comparison_df["timestamp_us"].iloc[-1] - comparison_df["timestamp_us"].iloc[0]) / 1e6
        delta = cmp_speed - ref_speed
        return LapDelta(
            reference_lap=reference_lap,
            comparison_lap=comparison_lap,
            delta_time_s=round(cmp_time - ref_time, 3),
            mean_delta_speed_kmh=round(float(np.mean(delta)), 3),
            max_delta_speed_kmh=round(float(np.max(np.abs(delta))), 3),
            distance_fraction=[round(float(value), 6) for value in axis],
            delta_speed_kmh=[round(float(value), 3) for value in delta],
        )

    @staticmethod
    def _resample(frame: pd.DataFrame, axis: np.ndarray) -> np.ndarray:
        timestamps = frame["timestamp_us"].to_numpy(dtype=float)
        speeds = frame["speed_kmh"].to_numpy(dtype=float)
        elapsed = timestamps - timestamps[0]
        if elapsed[-1] <= 0 or np.any(np.diff(timestamps) <= 0):
            raise ValueError("Lap timestamps must increase")
        return np.interp(axis, elapsed / elapsed[-1], speeds)
