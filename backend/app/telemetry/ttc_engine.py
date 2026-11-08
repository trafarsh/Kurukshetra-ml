"""
Physics-Based Time-to-Contact (TTC) Engine for Driver Collision Awareness.

Governing Equations:
  closing_speed (m/s) = (previous_distance_m - current_distance_m) / elapsed_time_s
  if closing_speed > 0:
      time_to_contact (s) = current_distance_m / closing_speed
  else:
      time_to_contact = infinity (object moving away or stationary relative to kart)

Warning Threshold Zones:
  - SAFE:    TTC > 2.5s or closing_speed <= 0
  - CAUTION: 1.0s <= TTC <= 2.5s
  - DANGER:  TTC < 1.0s
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass
class TTCResult:
    distance_cm: float
    closing_speed_mps: float
    ttc_seconds: Optional[float]
    warning_level: str  # SAFE, CAUTION, DANGER
    latency_ms: float


class TTCEngine:
    def __init__(
        self,
        caution_threshold_s: float = 2.5,
        danger_threshold_s: float = 1.0,
        max_valid_distance_cm: float = 500.0,
        min_valid_distance_cm: float = 5.0,
    ):
        self.caution_threshold = caution_threshold_s
        self.danger_threshold = danger_threshold_s
        self.max_distance = max_valid_distance_cm
        self.min_distance = min_valid_distance_cm

        self._prev_distance_m: Optional[float] = None
        self._prev_timestamp_us: Optional[int] = None

    def reset(self) -> None:
        """Reset internal history filter."""
        self._prev_distance_m = None
        self._prev_timestamp_us = None

    def update(self, distance_cm: float, timestamp_us: int) -> TTCResult:
        """
        Process a new distance observation and compute closing speed and TTC.
        
        Args:
            distance_cm: Ultrasonic / ToF sensor reading in centimeters.
            timestamp_us: Timestamp from monotonic clock in microseconds.
            
        Returns:
            TTCResult with closing speed, TTC in seconds, and warning zone.
        """
        # Validate sensor boundaries
        if distance_cm < self.min_distance or distance_cm > self.max_distance:
            # Out of bounds or sensor dropout
            return TTCResult(
                distance_cm=distance_cm,
                closing_speed_mps=0.0,
                ttc_seconds=None,
                warning_level="SAFE",
                latency_ms=0.0,
            )

        curr_distance_m = distance_cm / 100.0

        if self._prev_distance_m is None or self._prev_timestamp_us is None:
            self._prev_distance_m = curr_distance_m
            self._prev_timestamp_us = timestamp_us
            return TTCResult(
                distance_cm=distance_cm,
                closing_speed_mps=0.0,
                ttc_seconds=None,
                warning_level="SAFE",
                latency_ms=0.0,
            )

        dt_s = (timestamp_us - self._prev_timestamp_us) / 1_000_000.0
        if dt_s <= 0.0 or dt_s > 1.0:  # Gap or clock reset
            self._prev_distance_m = curr_distance_m
            self._prev_timestamp_us = timestamp_us
            return TTCResult(
                distance_cm=distance_cm,
                closing_speed_mps=0.0,
                ttc_seconds=None,
                warning_level="SAFE",
                latency_ms=0.0,
            )

        # Closing speed: positive when distance is decreasing
        closing_speed = (self._prev_distance_m - curr_distance_m) / dt_s

        self._prev_distance_m = curr_distance_m
        self._prev_timestamp_us = timestamp_us

        # TTC Calculation
        if closing_speed > 0.1:  # Threshold noise filter at 0.1 m/s
            ttc = curr_distance_m / closing_speed
        else:
            ttc = None

        # Warning evaluation
        if ttc is not None:
            if ttc < self.danger_threshold:
                warning_level = "DANGER"
            elif ttc <= self.caution_threshold:
                warning_level = "CAUTION"
            else:
                warning_level = "SAFE"
        else:
            warning_level = "SAFE"

        return TTCResult(
            distance_cm=distance_cm,
            closing_speed_mps=round(closing_speed, 2),
            ttc_seconds=round(ttc, 2) if ttc is not None else None,
            warning_level=warning_level,
            latency_ms=dt_s * 1000.0,
        )
