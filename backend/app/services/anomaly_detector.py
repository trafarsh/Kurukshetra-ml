"""Engine anomaly detector service and model registry integration."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
from typing import Any

import numpy as np

from app.core.config import settings


def _detector_class() -> type[Any]:
    module_path = Path(__file__).parents[3] / "machine-learning" / "models" / "engine_anomaly.py"
    spec = importlib.util.spec_from_file_location("kurukshetra_engine_anomaly", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load anomaly detector from {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module.EngineAnomalyDetector


class EngineAnomalyService:
    def __init__(self, model_path: str | None = None):
        detector_class = _detector_class()
        self.detector_class = detector_class
        self.model_path = Path(model_path or settings.ML_MODELS_DIR) / "engine_anomaly.joblib"
        self.detector = self._load_or_create()

    def _load_or_create(self) -> Any:
        if self.model_path.is_file():
            return self.detector_class.load(str(self.model_path))
        return self.detector_class()

    def train(self, samples: list[list[float]]) -> int:
        values = np.asarray(samples, dtype=float)
        if values.ndim != 2 or values.shape[1] != 4 or values.shape[0] < 10:
            raise ValueError("Training samples must contain at least 10 rows of [rpm, temp_c, speed_kmh, accel_x_g]")
        self.detector.fit(values)
        self.detector.save(str(self.model_path))
        return int(values.shape[0])

    def predict(self, rpm: float, temp_c: float, speed_kmh: float, accel_x_g: float) -> Any:
        return self.detector.predict_sample(rpm, temp_c, speed_kmh, accel_x_g)


anomaly_service = EngineAnomalyService()
