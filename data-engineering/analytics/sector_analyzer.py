"""
Sector Segmentation & Corner Analysis Engine.

Computes:
- Sector split times (S1, S2, S3)
- Corner apex speeds (minimum speed during turn)
- Acceleration out of corners
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional
import pandas as pd


@dataclass
class SectorMetrics:
    sector_number: int
    sector_time_s: float
    entry_speed_kmh: float
    exit_speed_kmh: float
    min_speed_kmh: float
    max_speed_kmh: float
    avg_throttle_pct: float
    max_lateral_g: float


class SectorAnalyzer:
    def __init__(self, sector_fractions: tuple[float, float, float] = (0.33, 0.33, 0.34)):
        self.sector_fractions = sector_fractions

    def analyze_lap_sectors(self, lap_df: pd.DataFrame) -> List[SectorMetrics]:
        """Divide lap telemetry into 3 sectors and compute cornering and split statistics."""
        if len(lap_df) < 10:
            return []

        n = len(lap_df)
        s1_end = int(n * self.sector_fractions[0])
        s2_end = int(n * (self.sector_fractions[0] + self.sector_fractions[1]))

        segments = [
            (1, lap_df.iloc[:s1_end]),
            (2, lap_df.iloc[s1_end:s2_end]),
            (3, lap_df.iloc[s2_end:]),
        ]

        metrics = []
        for sec_num, sec_df in segments:
            if len(sec_df) < 2:
                continue

            dt_s = (sec_df.iloc[-1]["timestamp_us"] - sec_df.iloc[0]["timestamp_us"]) / 1_000_000.0

            metrics.append(
                SectorMetrics(
                    sector_number=sec_num,
                    sector_time_s=round(dt_s, 2),
                    entry_speed_kmh=round(float(sec_df.iloc[0]["speed_kmh"]), 1),
                    exit_speed_kmh=round(float(sec_df.iloc[-1]["speed_kmh"]), 1),
                    min_speed_kmh=round(float(sec_df["speed_kmh"].min()), 1),
                    max_speed_kmh=round(float(sec_df["speed_kmh"].max()), 1),
                    avg_throttle_pct=round(float(sec_df["throttle_percent"].mean()), 1),
                    max_lateral_g=round(float(sec_df["accel_y_g"].abs().max()), 2),
                )
            )

        return metrics

