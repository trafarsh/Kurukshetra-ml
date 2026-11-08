"""Coverage for Phase 4 quality, lap detection, and comparison features."""
import numpy as np
import pandas as pd

from analytics.lap_comparison import LapComparison
from analytics.lap_detector import LapDetector
from preprocessing.quality_report import DataQualityAnalyzer


def _lap_frame(offset_us=0, speed=50.0):
    return pd.DataFrame({
        "timestamp_us": np.arange(0, 20_000_001, 100_000, dtype=np.int64) + offset_us,
        "speed_kmh": np.full(201, speed),
        "engine_rpm": np.full(201, 6000),
        "accel_y_g": np.zeros(201),
    })


def test_quality_report_counts_duplicates_gaps_and_outliers():
    raw = pd.DataFrame({"timestamp_us": [0, 50_000, 50_000, 250_000], "speed_kmh": [10, 11, None, 12]})
    report = DataQualityAnalyzer().summarize(raw, rejected_outliers=1)
    assert report.duplicate_timestamps == 1
    assert report.timestamp_gaps == 1
    assert report.rejected_outliers == 1
    assert report.completeness_pct == 75.0


def test_manual_lap_detection_creates_metrics():
    frame = pd.concat([_lap_frame(), _lap_frame(offset_us=20_100_000)], ignore_index=True)
    laps = LapDetector().detect_manual_laps(frame, [0, 200, 400])
    assert len(laps) == 2
    assert laps[0].lap_time_s == 20.0


def test_lap_comparison_returns_delta_trace():
    reference = _lap_frame(speed=50.0)
    comparison = _lap_frame(speed=55.0)
    result = LapComparison(points=10).compare(reference, comparison)
    assert result.delta_time_s == 0.0
    assert result.max_delta_speed_kmh == 5.0
    assert len(result.delta_speed_kmh) == 10
