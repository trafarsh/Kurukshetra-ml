"""Lap-time prediction model with session-aware validation."""
from __future__ import annotations

import os
from dataclasses import dataclass

import joblib
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GroupKFold
from sklearn.metrics import mean_absolute_error, root_mean_squared_error


@dataclass(frozen=True)
class LapTimePrediction:
    lap_time_s: float
    model_version: str = "v1.0.0"


class LapTimePredictor:
    VERSION = "v1.0.0"
    FEATURE_COUNT = 8

    def __init__(self, random_state: int = 42):
        self.model = RandomForestRegressor(
            n_estimators=150,
            min_samples_leaf=2,
            random_state=random_state,
            n_jobs=-1,
        )
        self.is_fitted = False

    def fit(self, X: np.ndarray, y: np.ndarray) -> "LapTimePredictor":
        features = np.asarray(X, dtype=float)
        targets = np.asarray(y, dtype=float)
        if features.ndim != 2 or features.shape[1] != self.FEATURE_COUNT:
            raise ValueError(f"Features must have shape (N, {self.FEATURE_COUNT})")
        if targets.ndim != 1 or len(targets) != len(features) or len(targets) < 4:
            raise ValueError("Targets must contain one lap time for each of at least 4 rows")
        self.model.fit(features, targets)
        self.is_fitted = True
        return self

    def validate_grouped(self, X: np.ndarray, y: np.ndarray, groups: np.ndarray) -> dict[str, float]:
        """Evaluate without allowing laps from one session into both folds."""
        features = np.asarray(X, dtype=float)
        targets = np.asarray(y, dtype=float)
        session_ids = np.asarray(groups)
        if len(features) != len(targets) or len(targets) != len(session_ids):
            raise ValueError("X, y, and groups must have equal lengths")
        if len(np.unique(session_ids)) < 2:
            raise ValueError("At least two sessions are required for grouped validation")
        predictions = np.empty(len(targets), dtype=float)
        splitter = GroupKFold(n_splits=min(5, len(np.unique(session_ids))))
        for train, test in splitter.split(features, targets, session_ids):
            fold = LapTimePredictor()
            fold.fit(features[train], targets[train])
            predictions[test] = fold.model.predict(features[test])
        return {
            "mae_s": round(float(mean_absolute_error(targets, predictions)), 4),
            "rmse_s": round(float(root_mean_squared_error(targets, predictions)), 4),
        }

    def predict(self, features: np.ndarray) -> LapTimePrediction:
        if not self.is_fitted:
            raise RuntimeError("Lap-time predictor must be fitted before prediction")
        values = np.asarray(features, dtype=float).reshape(1, -1)
        if values.shape[1] != self.FEATURE_COUNT:
            raise ValueError(f"Features must contain {self.FEATURE_COUNT} values")
        return LapTimePrediction(round(float(self.model.predict(values)[0]), 3), self.VERSION)

    def save(self, filepath: str) -> None:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        joblib.dump({"model": self.model, "is_fitted": self.is_fitted, "version": self.VERSION}, filepath)

    @classmethod
    def load(cls, filepath: str) -> "LapTimePredictor":
        data = joblib.load(filepath)
        predictor = cls()
        predictor.model = data["model"]
        predictor.is_fitted = data["is_fitted"]
        return predictor
