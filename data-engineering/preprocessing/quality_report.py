"""Data quality metrics for raw and cleaned telemetry sessions."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import pandas as pd


@dataclass(frozen=True)
class DataQualityReport:
    record_count: int
    duration_s: float
    completeness_pct: float
    missing_values: int
    duplicate_timestamps: int
    timestamp_gaps: int
    rejected_outliers: int
    noise_ratio_pct: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class DataQualityAnalyzer:
    """Generate an auditable quality summary without changing telemetry data."""

    def __init__(self, expected_interval_us: int = 50_000, gap_tolerance: float = 3.0):
        self.expected_interval_us = expected_interval_us
        self.gap_tolerance = gap_tolerance

    def summarize(
        self,
        raw_df: pd.DataFrame,
        cleaned_df: pd.DataFrame | None = None,
        rejected_outliers: int = 0,
    ) -> DataQualityReport:
        if raw_df.empty:
            return DataQualityReport(0, 0.0, 0.0, 0, 0, 0, rejected_outliers, 0.0)
        if "timestamp_us" not in raw_df.columns:
            raise ValueError("Telemetry data must contain a timestamp_us column")

        timestamps = pd.to_numeric(raw_df["timestamp_us"], errors="coerce")
        valid_timestamps = timestamps.dropna()
        duration_s = (
            float(valid_timestamps.iloc[-1] - valid_timestamps.iloc[0]) / 1_000_000.0
            if len(valid_timestamps) > 1
            else 0.0
        )
        deltas = valid_timestamps.sort_values().diff().dropna()
        gap_limit = self.expected_interval_us * self.gap_tolerance
        timestamp_gaps = int((deltas > gap_limit).sum())
        duplicate_timestamps = int(timestamps.duplicated().sum())
        missing_values = int(raw_df.isna().sum().sum())
        total_values = max(raw_df.size, 1)
        cleaned_count = len(cleaned_df) if cleaned_df is not None else len(raw_df.drop_duplicates("timestamp_us"))
        completeness_pct = round(cleaned_count / len(raw_df) * 100.0, 2)
        noise_ratio_pct = round(rejected_outliers / len(raw_df) * 100.0, 2)
        return DataQualityReport(
            record_count=len(raw_df),
            duration_s=round(duration_s, 3),
            completeness_pct=completeness_pct,
            missing_values=missing_values,
            duplicate_timestamps=duplicate_timestamps,
            timestamp_gaps=timestamp_gaps,
            rejected_outliers=rejected_outliers,
            noise_ratio_pct=noise_ratio_pct,
        )
