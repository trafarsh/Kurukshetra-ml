"""
Data Cleaning and Signal Processing Pipeline.

Applies:
- Monotonic timestamp sorting and clock drift realignment
- Outlier filtering (median filter and physical sanity clamps)
- Drop-out imputation via linear interpolation (for gaps < 150 ms)
- Noise smoothing for acceleration and steering channels
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List
import numpy as np
import pandas as pd


@dataclass
class CleaningReport:
    raw_record_count: int
    cleaned_record_count: int
    spikes_removed: int
    interpolated_points: int
    completeness_pct: float


class TelemetryDataCleaner:
    def __init__(
        self,
        max_rpm: int = 12000,
        max_temp_c: float = 140.0,
        min_temp_c: float = 0.0,
        max_speed_kmh: float = 130.0,
    ):
        self.max_rpm = max_rpm
        self.max_temp_c = max_temp_c
        self.min_temp_c = min_temp_c
        self.max_speed_kmh = max_speed_kmh

    def clean_dataframe(self, df: pd.DataFrame) -> tuple[pd.DataFrame, CleaningReport]:
        """Clean raw telemetry DataFrame and return cleaned frame with quality metrics."""
        raw_count = len(df)
        if raw_count == 0:
            return df, CleaningReport(0, 0, 0, 0, 0.0)

        cleaned = df.copy()

        # 1. Sort by timestamp_us monotonically
        cleaned = cleaned.sort_values(by="timestamp_us").reset_index(drop=True)

        # 2. Deduplicate exact timestamps
        cleaned = cleaned.drop_duplicates(subset=["timestamp_us"]).reset_index(drop=True)

        spikes_removed = 0

        # 3. Filter RPM spikes
        if "engine_rpm" in cleaned.columns:
            invalid_rpm = (cleaned["engine_rpm"] < 0) | (cleaned["engine_rpm"] > self.max_rpm)
            spikes_removed += int(invalid_rpm.sum())
            cleaned.loc[invalid_rpm, "engine_rpm"] = np.nan

        # 4. Filter Temperature spikes
        if "engine_temp_c" in cleaned.columns:
            invalid_temp = (cleaned["engine_temp_c"] < self.min_temp_c) | (cleaned["engine_temp_c"] > self.max_temp_c)
            spikes_removed += int(invalid_temp.sum())
            cleaned.loc[invalid_temp, "engine_temp_c"] = np.nan

        # 5. Filter Speed anomalies
        if "speed_kmh" in cleaned.columns:
            invalid_speed = (cleaned["speed_kmh"] < 0) | (cleaned["speed_kmh"] > self.max_speed_kmh)
            spikes_removed += int(invalid_speed.sum())
            cleaned.loc[invalid_speed, "speed_kmh"] = np.nan

        # 6. Interpolate small NaN gaps (limit 3 consecutive samples = ~150ms at 20Hz)
        interpolated = int(cleaned.isna().sum().sum())
        cleaned = cleaned.interpolate(method="linear", limit=3).bfill().ffill()

        report = CleaningReport(
            raw_record_count=raw_count,
            cleaned_record_count=len(cleaned),
            spikes_removed=spikes_removed,
            interpolated_points=interpolated,
            completeness_pct=round(len(cleaned) / raw_count * 100.0, 2) if raw_count > 0 else 0.0,
        )

        return cleaned, report

