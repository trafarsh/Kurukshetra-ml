"""Tests for the engine anomaly inference API."""
import numpy as np


def test_engine_anomaly_prediction_uses_rule_fallback(client):
    response = client.post(
        "/api/v1/ml/anomaly/predict",
        json={"rpm": 11000, "temp_c": 80, "speed_kmh": 20, "accel_x_g": 0.1},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["is_anomaly"] is True
    assert payload["model_version"] == "v1.0.0"


def test_engine_anomaly_training_and_prediction(client, tmp_path, monkeypatch):
    from app.services import anomaly_detector

    service = anomaly_detector.EngineAnomalyService(str(tmp_path))
    monkeypatch.setattr(anomaly_detector, "anomaly_service", service)
    monkeypatch.setattr("app.api.routes.ml.anomaly_service", service)
    samples = np.tile([[5000.0, 80.0, 50.0, 0.1]], (12, 1)).tolist()
    response = client.post("/api/v1/ml/anomaly/train", json={"samples": samples})
    assert response.status_code == 201
    assert (tmp_path / "engine_anomaly.joblib").is_file()
