"""Driver behaviour classifier for telemetry-derived session features."""
from __future__ import annotations

import os
from dataclasses import dataclass

import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier


@dataclass(frozen=True)
class DriverBehaviourPrediction:
    behaviour: str
    confidence: float
    model_version: str = "v1.0.0"


class DriverBehaviourClassifier:
    VERSION = "v1.0.0"
    FEATURE_COUNT = 5

    def __init__(self, random_state: int = 42):
        self.model = RandomForestClassifier(
            n_estimators=120,
            min_samples_leaf=2,
            random_state=random_state,
            n_jobs=-1,
        )
        self.is_fitted = False

    def fit(self, X: np.ndarray, labels: list[str] | np.ndarray) -> "DriverBehaviourClassifier":
        features = np.asarray(X, dtype=float)
        targets = np.asarray(labels)
        if features.ndim != 2 or features.shape[1] != self.FEATURE_COUNT:
            raise ValueError(f"Features must have shape (N, {self.FEATURE_COUNT})")
        if len(features) < 6 or len(targets) != len(features) or len(np.unique(targets)) < 2:
            raise ValueError("Training requires at least 6 rows and two behaviour classes")
        self.model.fit(features, targets)
        self.is_fitted = True
        return self

    def predict(self, features: np.ndarray) -> DriverBehaviourPrediction:
        if not self.is_fitted:
            raise RuntimeError("Driver behaviour classifier must be fitted before prediction")
        values = np.asarray(features, dtype=float).reshape(1, -1)
        if values.shape[1] != self.FEATURE_COUNT:
            raise ValueError(f"Features must contain {self.FEATURE_COUNT} values")
        probabilities = self.model.predict_proba(values)[0]
        index = int(np.argmax(probabilities))
        return DriverBehaviourPrediction(
            behaviour=str(self.model.classes_[index]),
            confidence=round(float(probabilities[index]), 4),
            model_version=self.VERSION,
        )

    def save(self, filepath: str) -> None:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        joblib.dump({"model": self.model, "is_fitted": self.is_fitted, "version": self.VERSION}, filepath)

    @classmethod
    def load(cls, filepath: str) -> "DriverBehaviourClassifier":
        data = joblib.load(filepath)
        classifier = cls()
        classifier.model = data["model"]
        classifier.is_fitted = data["is_fitted"]
        return classifier
