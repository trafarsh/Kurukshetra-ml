"""
MODEL 1: Engine Anomaly Detector (Isolation Forest).

Inputs:
- engine_rpm
- engine_temp_c
- speed_kmh
- accel_x_g (longitudinal acceleration)

Objective:
Detect thermal runaway, over-revving, ignition misfires, and abnormal operating patterns
without labeling standard pit idling or gear-change drops as mechanical faults.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List, Tuple
import joblib
import numpy as np
from sklearn.ensemble import IsolationForest


@dataclass
class AnomalyResult:
    is_anomaly: bool
    anomaly_score: float  # Negative is anomalous, positive is normal
    model_version: str = "v1.0.0"


class EngineAnomalyDetector:
    VERSION = "v1.0.0"

    def __init__(self, contamination: float = 0.03, random_state: int = 42):
        self.model = IsolationForest(
            contamination=contamination,
            random_state=random_state,
            n_estimators=100,
            n_jobs=-1,
        )
        self.is_fitted = False

    def fit(self, X: np.ndarray) -> EngineAnomalyDetector:
        """
        Fit Isolation Forest on normal baseline telemetry.
        X shape: (N, 4) -> [rpm, temp_c, speed_kmh, accel_x_g]
        """
        self.model.fit(X)
        self.is_fitted = True
        return self

    def predict_sample(
        self,
        rpm: float,
        temp_c: float,
        speed_kmh: float,
        accel_x_g: float,
    ) -> AnomalyResult:
        """Predict whether an instantaneous engine operating state is anomalous."""
        if not self.is_fitted:
            # Rule-based fallback if untrained
            is_anomaly = rpm > 9800 or temp_c > 110.0 or (rpm > 7000 and speed_kmh < 5.0)
            score = -0.5 if is_anomaly else 0.5
            return AnomalyResult(is_anomaly=is_anomaly, anomaly_score=score, model_version=self.VERSION)

        features = np.array([[rpm, temp_c, speed_kmh, accel_x_g]])
        pred = self.model.predict(features)[0]  # 1 for inlier, -1 for outlier
        score = float(self.model.decision_function(features)[0])

        return AnomalyResult(
            is_anomaly=(pred == -1),
            anomaly_score=round(score, 4),
            model_version=self.VERSION,
        )

    def save(self, filepath: str) -> None:
        """Serialize trained model to joblib."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        joblib.dump({"model": self.model, "is_fitted": self.is_fitted, "version": self.VERSION}, filepath)

    @classmethod
    def load(cls, filepath: str) -> EngineAnomalyDetector:
        """Load serialized model."""
        data = joblib.load(filepath)
        detector = cls()
        detector.model = data["model"]
        detector.is_fitted = data["is_fitted"]
        return detector

