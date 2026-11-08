"""Unit tests for Phase 3 Telemetry Ingestion and Protocols."""
import pytest
from app.telemetry.packet_decoder import PacketDecoder
from app.telemetry.ttc_engine import TTCEngine
from app.telemetry.sd_importer import SDCardImporter


def test_packet_encode_decode_roundtrip():
    """Verify that encoded values can be recovered accurately through 16-byte binary framing."""
    raw = PacketDecoder.encode(
        timestamp_ms=124500,
        speed_kmh=74.35,
        engine_rpm=7820,
        engine_temp_c=91.0,
        steering_deg=-18.0,
        throttle_pct=85.0,
        accel_x_g=0.42,
        accel_y_g=-1.12,
        ttc_seconds=1.45,
        warning_level="CAUTION",
        sensor_fault=False,
    )

    assert len(raw) == 16

    decoded = PacketDecoder.decode(raw)
    assert decoded.timestamp_ms == 124500
    assert abs(decoded.speed_kmh - 74.35) < 0.02
    assert decoded.engine_rpm == 7820
    assert decoded.engine_temp_c == 91.0
    assert decoded.steering_angle_deg == -18.0
    assert decoded.throttle_percent == 85.0
    assert abs(decoded.accel_x_g - 0.42) < 0.03
    assert abs(decoded.accel_y_g - -1.12) < 0.03
    assert decoded.ttc_seconds is not None
    assert abs(decoded.ttc_seconds - 1.45) < 0.02
    assert decoded.warning_level == "CAUTION"
    assert decoded.sensor_fault is False
    assert decoded.is_valid_checksum is True


def test_packet_checksum_detects_corruption():
    """Verify corrupted byte triggers checksum invalid flag."""
    raw = bytearray(
        PacketDecoder.encode(
            timestamp_ms=5000,
            speed_kmh=60.0,
            engine_rpm=6000,
            engine_temp_c=85.0,
            steering_deg=0.0,
            throttle_pct=100.0,
            accel_x_g=0.5,
            accel_y_g=0.0,
            ttc_seconds=None,
            warning_level="SAFE",
        )
    )

    # Corrupt speed byte
    raw[4] ^= 0xFF

    decoded = PacketDecoder.decode(bytes(raw))
    assert decoded.is_valid_checksum is False


def test_ttc_engine_warning_zones():
    """Test closing speed and TTC calculation across SAFE, CAUTION, and DANGER zones."""
    ttc = TTCEngine(caution_threshold_s=2.5, danger_threshold_s=1.0)

    # 1. First sample establishes baseline
    res1 = ttc.update(distance_cm=400.0, timestamp_us=100_000)
    assert res1.warning_level == "SAFE"
    assert res1.ttc_seconds is None

    # 2. Distance drops from 4.0m to 3.0m in 0.5s -> closing speed = 2.0 m/s
    # TTC = 3.0m / 2.0m/s = 1.5s -> CAUTION (between 1.0 and 2.5s)
    res2 = ttc.update(distance_cm=300.0, timestamp_us=600_000)
    assert res2.closing_speed_mps == 2.0
    assert res2.ttc_seconds == 1.5
    assert res2.warning_level == "CAUTION"

    # 3. Distance drops from 3.0m to 1.6m in 0.2s -> closing speed = 7.0 m/s
    # TTC = 1.6m / 7.0m/s = 0.23s -> DANGER (< 1.0s)
    res3 = ttc.update(distance_cm=160.0, timestamp_us=800_000)
    assert res3.closing_speed_mps == 7.0
    assert res3.ttc_seconds is not None
    assert res3.ttc_seconds < 1.0
    assert res3.warning_level == "DANGER"

    # 4. Object moving away (distance increases from 1.6m to 2.5m) -> SAFE
    res4 = ttc.update(distance_cm=250.0, timestamp_us=1_000_000)
    assert res4.closing_speed_mps <= 0.0
    assert res4.ttc_seconds is None
    assert res4.warning_level == "SAFE"


def test_sd_card_csv_importer():
    """Test CSV log parser, noise filtering, and data quality metrics."""
    importer = SDCardImporter()

    csv_data = """timestamp_us,speed_kmh,engine_rpm,engine_temp_c,steering_deg,throttle_pct,accel_x_g,accel_y_g,ttc_seconds,warning_level
1000000,45.2,5200,82.5,2.1,80.0,0.32,0.12,3.2,SAFE
1020000,47.8,5500,83.0,-1.4,95.0,0.45,0.08,2.8,SAFE
1040000,50.1,28000,83.4,-1.2,100.0,0.51,0.05,2.6,SAFE
1060000,52.4,6100,83.9,0.0,100.0,0.48,0.00,,SAFE
"""
    # Notice row 3 has an impossible RPM spike of 28,000 (IC engine rev limit is ~10,000)
    records, quality = importer.parse_csv(csv_data)

    assert quality.total_records == 4
    assert quality.valid_records == 3
    assert quality.rejected_records == 1
    assert "Impossible RPM 28000" in quality.anomalies[0]
    assert len(records) == 3
    assert records[0]["speed_kmh"] == 45.2
