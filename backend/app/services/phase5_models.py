"""Services for the remaining Phase 5 predictive models."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

import numpy as np

from app.core.config import settings


def _load_class(filename: str, class_name: str) -> type[Any]:
    path = Path(__file__).parents[3] / "machine-learning" / "models" / filename
    spec = importlib.util.spec_from_file_location(f"kurukshetra_{class_name.lower()}", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load model from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return getattr(module, class_name)


LapTimePredictor = _load_class("lap_time_predictor.py", "LapTimePredictor")
DriverBehaviourClassifier = _load_class("driver_behavior.py", "DriverBehaviourClassifier")
DynamicGripEstimator = _load_class("dynamic_grip.py", "DynamicGripEstimator")


class Phase5ModelService:
    def __init__(self, model_dir: str | None = None):
        self.model_dir = Path(model_dir or settings.ML_MODELS_DIR)
        self.lap_predictor = self._load_or_create(LapTimePredictor, "lap_time_predictor.joblib")
        self.behaviour_classifier = self._load_or_create(
            DriverBehaviourClassifier, "driver_behaviour.joblib"
        )
        self.grip_estimator = DynamicGripEstimator()

    def _load_or_create(self, model_class: type[Any], filename: str) -> Any:
        path = self.model_dir / filename
        return model_class.load(str(path)) if path.is_file() else model_class()

    def predict_lap_time(self, features: list[float]) -> Any:
        return self.lap_predictor.predict(np.asarray(features, dtype=float))

    def predict_behaviour(self, features: list[float]) -> Any:
        return self.behaviour_classifier.predict(np.asarray(features, dtype=float))

    def estimate_grip(
        self,
        lateral_g: float,
        speed_kmh: float | None,
        radius_m: float | None,
        sensor_quality: float,
    ) -> Any:
        return self.grip_estimator.estimate(lateral_g, speed_kmh, radius_m, sensor_quality)


phase5_service = Phase5ModelService()
