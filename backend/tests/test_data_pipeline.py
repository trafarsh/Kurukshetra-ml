"""Unit tests for Data Engineering Cleaning & Analytics."""
import numpy as np
import pandas as pd
import pytest
from preprocessing.cleaning_pipeline import TelemetryDataCleaner
from analytics.sector_analyzer import SectorAnalyzer


def test_data_cleaner_spike_rejection():
    cleaner = TelemetryDataCleaner(max_rpm=10000, max_temp_c=120.0)

    raw_data = {
        "timestamp_us": [1000, 2000, 3000, 4000, 5000],
        "speed_kmh": [40.0, 42.0, 44.0, 46.0, 48.0],
        "engine_rpm": [5000, 5200, 35000, 5600, 5800],  # 35,000 is impossible spike
        "engine_temp_c": [80.0, 81.0, 82.0, 240.0, 84.0],  # 240 is thermal sensor spike
    }
    df = pd.DataFrame(raw_data)
    cleaned, report = cleaner.clean_dataframe(df)

    assert report.spikes_removed == 2
    assert cleaned["engine_rpm"].max() <= 10000
    assert cleaned["engine_temp_c"].max() <= 120.0


def test_sector_analyzer_splits():
    analyzer = SectorAnalyzer()

    # 100 samples simulating a 45 second lap
    timestamps = np.linspace(1_000_000, 46_000_000, 100, dtype=np.int64)
    speeds = 50.0 + 20.0 * np.sin(np.linspace(0, np.pi * 2, 100))
    throttles = np.clip(speeds * 1.5, 0, 100)
    ay = 1.1 * np.cos(np.linspace(0, np.pi * 2, 100))

    df = pd.DataFrame({
        "timestamp_us": timestamps,
        "speed_kmh": speeds,
        "throttle_percent": throttles,
        "accel_y_g": ay,
    })

    sectors = analyzer.analyze_lap_sectors(df)
    assert len(sectors) == 3
    assert sectors[0].sector_number == 1
    assert sectors[1].sector_number == 2
    assert sectors[2].sector_number == 3
    assert sectors[0].sector_time_s > 0
