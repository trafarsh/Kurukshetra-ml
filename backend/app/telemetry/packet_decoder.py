"""
16-Byte Compact Binary Telemetry Packet Decoder & Encoder for ESP32 Gateway.

Packet Specification (16 bytes total):
- [0..3]   uint32_t timestamp_ms       (4 bytes, LE)
- [4..5]   uint16_t speed_raw          (2 bytes, LE) -> speed_kmh = raw / 100.0
- [6..7]   uint16_t engine_rpm         (2 bytes, LE) -> rpm
- [8]      uint8_t  engine_temp_c      (1 byte)      -> temp °C
- [9]      int8_t   steering_deg       (1 byte, signed) -> steering angle degrees
- [10]     uint8_t  throttle_pct       (1 byte)      -> throttle 0..100 %
- [11]     int8_t   accel_x_raw        (1 byte, signed) -> accel_x = raw / 50.0 g
- [12]     int8_t   accel_y_raw        (1 byte, signed) -> accel_y = raw / 50.0 g
- [13..14] uint16_t ttc_raw            (2 bytes, LE) -> ttc_seconds = raw / 100.0 (65535 = infinity)
- [15]     uint8_t  flags_checksum     (1 byte)      -> bits 0..1: warning (0=SAFE, 1=CAUTION, 2=DANGER)
                                                        bits 2..3: sensor status (0=OK, 1=FAULT)
                                                        bits 4..7: checksum of bytes 0..14
"""
from __future__ import annotations

import struct
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class DecodedTelemetryPacket:
    timestamp_ms: int
    speed_kmh: float
    engine_rpm: int
    engine_temp_c: float
    steering_angle_deg: float
    throttle_percent: float
    accel_x_g: float
    accel_y_g: float
    ttc_seconds: Optional[float]
    warning_level: str  # SAFE, CAUTION, DANGER
    sensor_fault: bool
    is_valid_checksum: bool


class PacketDecoder:
    PACKET_SIZE = 16
    FIRST_15_FORMAT = "<IHHBbBbbH"

    @staticmethod
    def calculate_checksum(data: bytes) -> int:
        """Compute 4-bit checksum over the first 15 bytes."""
        return sum(data[:15]) & 0x0F

    @classmethod
    def encode(
        cls,
        timestamp_ms: int,
        speed_kmh: float,
        engine_rpm: int,
        engine_temp_c: float,
        steering_deg: float,
        throttle_pct: float,
        accel_x_g: float,
        accel_y_g: float,
        ttc_seconds: Optional[float],
        warning_level: str = "SAFE",
        sensor_fault: bool = False,
    ) -> bytes:
        """Encode physical values into the canonical 16-byte binary frame."""
        raw_speed = max(0, min(65535, int(round(speed_kmh * 100))))
        raw_rpm = max(0, min(65535, int(engine_rpm)))
        raw_temp = max(0, min(255, int(round(engine_temp_c))))
        raw_steering = max(-128, min(127, int(round(steering_deg))))
        raw_throttle = max(0, min(100, int(round(throttle_pct))))
        raw_ax = max(-128, min(127, int(round(accel_x_g * 50))))
        raw_ay = max(-128, min(127, int(round(accel_y_g * 50))))

        if ttc_seconds is None or ttc_seconds >= 655.35:
            raw_ttc = 65535
        else:
            raw_ttc = max(0, min(65534, int(round(ttc_seconds * 100))))

        # Pack first 15 bytes
        first_15 = struct.pack(
            cls.FIRST_15_FORMAT,
            timestamp_ms & 0xFFFFFFFF,
            raw_speed,
            raw_rpm,
            raw_temp,
            raw_steering,
            raw_throttle,
            raw_ax,
            raw_ay,
            raw_ttc,
        )

        # Warning bits: 0=SAFE, 1=CAUTION, 2=DANGER
        warning_bits = 0
        if warning_level == "CAUTION":
            warning_bits = 1
        elif warning_level == "DANGER":
            warning_bits = 2

        fault_bit = 1 if sensor_fault else 0
        chk_nibble = cls.calculate_checksum(first_15)

        # byte 15: [bits 4..7: checksum] [bits 2..3: fault] [bits 0..1: warning]
        flags_byte = ((chk_nibble & 0x0F) << 4) | ((fault_bit & 0x03) << 2) | (warning_bits & 0x03)
        return first_15 + struct.pack("B", flags_byte)

    @classmethod
    def decode(cls, data: bytes) -> DecodedTelemetryPacket:
        """Decode a 16-byte raw frame with checksum validation."""
        if len(data) != cls.PACKET_SIZE:
            raise ValueError(f"Packet size mismatch: expected {cls.PACKET_SIZE} bytes, got {len(data)}")

        first_15 = data[:15]
        flags_byte = data[15]

        expected_chk = cls.calculate_checksum(first_15)
        actual_chk = (flags_byte >> 4) & 0x0F
        is_valid_checksum = expected_chk == actual_chk

        (
            ts_ms,
            raw_speed,
            raw_rpm,
            raw_temp,
            raw_steering,
            raw_throttle,
            raw_ax,
            raw_ay,
            raw_ttc,
        ) = struct.unpack(cls.FIRST_15_FORMAT, first_15)

        warning_bits = flags_byte & 0x03
        warning_map = {0: "SAFE", 1: "CAUTION", 2: "DANGER"}
        warning_level = warning_map.get(warning_bits, "SAFE")

        sensor_fault = bool((flags_byte >> 2) & 0x01)
        ttc_seconds = None if raw_ttc == 65535 else raw_ttc / 100.0

        return DecodedTelemetryPacket(
            timestamp_ms=ts_ms,
            speed_kmh=raw_speed / 100.0,
            engine_rpm=raw_rpm,
            engine_temp_c=float(raw_temp),
            steering_angle_deg=float(raw_steering),
            throttle_percent=float(raw_throttle),
            accel_x_g=raw_ax / 50.0,
            accel_y_g=raw_ay / 50.0,
            ttc_seconds=ttc_seconds,
            warning_level=warning_level,
            sensor_fault=sensor_fault,
            is_valid_checksum=is_valid_checksum,
        )
