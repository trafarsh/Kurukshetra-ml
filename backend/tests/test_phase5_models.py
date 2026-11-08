"""Tests for Phase 5 predictive models."""
import numpy as np

from app.services.phase5_models import (
    DriverBehaviourClassifier,
    DynamicGripEstimator,
    LapTimePredictor,
)


def test_lap_time_predictor_supports_grouped_validation():
    features = np.tile(np.arange(8, dtype=float), (6, 1))
    targets = np.array([42.0, 42.2, 44.0, 44.2, 46.0, 46.2])
    groups = np.array(["a", "a", "b", "b", "c", "c"])
    predictor = LapTimePredictor().fit(features, targets)
    metrics = predictor.validate_grouped(features, targets, groups)
    assert predictor.predict(features[0]).lap_time_s > 0
    assert set(metrics) == {"mae_s", "rmse_s"}


def test_driver_behaviour_classifier_predicts_known_class():
    features = np.array([
        [10, 0.4, 0.2, 1.0, 2.0],
        [11, 0.5, 0.2, 1.1, 2.1],
        [35, 1.5, 0.8, 4.0, 12.0],
        [36, 1.6, 0.9, 4.1, 12.5],
        [20, 0.8, 0.4, 2.0, 6.0],
        [21, 0.9, 0.5, 2.1, 6.2],
    ])
    classifier = DriverBehaviourClassifier().fit(
        features, ["smooth", "smooth", "aggressive", "aggressive", "balanced", "balanced"]
    )
    result = classifier.predict(features[0])
    assert result.behaviour == "smooth"
    assert 0 < result.confidence <= 1


def test_dynamic_grip_estimator_uses_conservative_measurement():
    estimate = DynamicGripEstimator().estimate(1.2, speed_kmh=36, radius_m=20)
    assert estimate.theoretical_mu is not None
    assert estimate.effective_mu == min(estimate.measured_mu, estimate.theoretical_mu)
