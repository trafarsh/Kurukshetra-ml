"""Dynamic tyre-grip estimator from lateral acceleration and corner geometry."""
from __future__ import annotations

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class GripEstimate:
    effective_mu: float
    measured_mu: float
    theoretical_mu: float | None
    confidence: float
    model_version: str = "v1.0.0"


class DynamicGripEstimator:
    VERSION = "v1.0.0"
    GRAVITY_MPS2 = 9.80665

    def estimate(
        self,
        lateral_g: float,
        speed_kmh: float | None = None,
        radius_m: float | None = None,
        sensor_quality: float = 1.0,
    ) -> GripEstimate:
        if not math.isfinite(lateral_g) or lateral_g < 0:
            raise ValueError("lateral_g must be a non-negative finite value")
        if speed_kmh is not None and (not math.isfinite(speed_kmh) or speed_kmh < 0):
            raise ValueError("speed_kmh must be a non-negative finite value")
        if radius_m is not None and (not math.isfinite(radius_m) or radius_m <= 0):
            raise ValueError("radius_m must be positive when supplied")
        if not 0 < sensor_quality <= 1:
            raise ValueError("sensor_quality must be between 0 and 1")

        measured_mu = float(lateral_g)
        theoretical_mu = None
        if speed_kmh is not None and radius_m is not None:
            speed_mps = speed_kmh / 3.6
            theoretical_mu = (speed_mps * speed_mps / radius_m) / self.GRAVITY_MPS2
        effective_mu = measured_mu if theoretical_mu is None else min(measured_mu, theoretical_mu)
        confidence = sensor_quality if theoretical_mu is None else min(sensor_quality, 0.9)
        return GripEstimate(
            effective_mu=round(effective_mu, 4),
            measured_mu=round(measured_mu, 4),
            theoretical_mu=None if theoretical_mu is None else round(theoretical_mu, 4),
            confidence=round(confidence, 4),
            model_version=self.VERSION,
        )
