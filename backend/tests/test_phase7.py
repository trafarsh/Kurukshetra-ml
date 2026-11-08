"""Tests for Phase 7 reporting, recommendations, and replay."""
from pathlib import Path

import pytest

from app.services.phase7 import RecommendationEngine, ReportExporter, SessionReplay


def test_recommendations_are_evidence_based():
    result = RecommendationEngine().recommend({
        "best_lap_time_s": 42.1,
        "max_engine_temp_c": 110,
        "anomaly_count": 2,
        "max_lateral_g": 1.0,
        "lap_consistency_pct": 100,
    })
    assert {item.priority for item in result} == {"HIGH"}
    assert all(item.evidence for item in result)


def test_report_exporter_writes_csv_and_pdf(tmp_path):
    paths = ReportExporter(str(tmp_path)).generate(
        "session/../debrief", [{"timestamp_us": 1, "speed_kmh": 20}], {"best_lap": 42.1}
    )
    assert Path(paths["csv_path"]).read_text(encoding="utf-8").startswith("speed_kmh,timestamp_us")
    assert Path(paths["pdf_path"]).read_bytes().startswith(b"%PDF-1.4")


def test_replay_is_timestamp_synchronized():
    frames = SessionReplay().prepare([
        {"timestamp_us": 2_000_000, "speed_kmh": 22},
        {"timestamp_us": 1_000_000, "speed_kmh": 20},
    ], speed=2)
    assert frames[0]["elapsed_s"] == 0
    assert frames[1]["elapsed_s"] == 0.5
    assert frames[1]["progress"] == 1


def test_replay_rejects_non_positive_speed():
    with pytest.raises(ValueError):
        SessionReplay().prepare([], speed=0)


def test_phase7_recommendation_endpoint(client):
    response = client.post(
        "/api/v1/recommendations",
        json={"metrics": {"best_lap_time_s": 42.1, "max_lateral_g": 1.0}},
    )
    assert response.status_code == 200
    assert response.json()["recommendations"][0]["category"] == "setup"
