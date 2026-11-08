"""
SD-Card Telemetry File Ingestion & Data Quality Engine.

Supports:
- CSV log parsing
- Raw 16-byte binary chunk parsing
- Timestamp monotonicity checks
- Impossible sensor value rejection (ignitions noise, sensor disconnects)
- SHA-256 raw file preservation
- Lap segmentation
"""
from __future__ import annotations

import csv
import hashlib
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from app.telemetry.packet_decoder import PacketDecoder, DecodedTelemetryPacket


@dataclass
class DataQualityReport:
    total_records: int
    valid_records: int
    rejected_records: int
    duplicate_timestamps: int
    clock_resets: int
    missing_data_pct: float
    duration_seconds: float
    laps_identified: int
    checksum_sha256: str
    anomalies: List[str] = field(default_factory=list)


class SDCardImporter:
    def __init__(self, raw_storage_dir: str = "./data/raw"):
        self.raw_storage_dir = raw_storage_dir
        os.makedirs(self.raw_storage_dir, exist_ok=True)

    def save_raw_file(self, filename: str, content: bytes) -> Tuple[str, str]:
        """Save an immutable copy of the raw log file and compute SHA-256."""
        sha256_hash = hashlib.sha256(content).hexdigest()
        timestamp_prefix = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp_prefix}_{filename}"
        dest_path = os.path.join(self.raw_storage_dir, safe_filename)

        with open(dest_path, "wb") as f:
            f.write(content)

        return dest_path, sha256_hash

    def parse_csv(self, file_content: str) -> Tuple[List[Dict[str, Any]], DataQualityReport]:
        """
        Parse CSV telemetry dump from MicroSD card.
        
        Expected headers:
          timestamp_us,speed_kmh,engine_rpm,engine_temp_c,steering_deg,throttle_pct,accel_x_g,accel_y_g,...
        """
        sha256_hash = hashlib.sha256(file_content.encode("utf-8")).hexdigest()
        lines = file_content.strip().splitlines()
        reader = csv.DictReader(lines)

        valid_records = []
        total = 0
        rejected = 0
        duplicates = 0
        clock_resets = 0
        last_ts = -1
        anomalies = []

        for row in reader:
            total += 1
            try:
                ts = int(row.get("timestamp_us", 0))
                speed = float(row.get("speed_kmh", 0.0))
                rpm = int(float(row.get("engine_rpm", 0)))
                temp = float(row.get("engine_temp_c", 0.0))
                steering = float(row.get("steering_deg", 0.0))
                throttle = float(row.get("throttle_pct", 0.0))
                ax = float(row.get("accel_x_g", 0.0))
                ay = float(row.get("accel_y_g", 0.0))

                # Sensor physical boundary validation
                if rpm < 0 or rpm > 16000:
                    rejected += 1
                    anomalies.append(f"Row {total}: Impossible RPM {rpm}")
                    continue
                if temp < -20.0 or temp > 220.0:
                    rejected += 1
                    anomalies.append(f"Row {total}: Impossible temp {temp}°C")
                    continue
                if speed < 0 or speed > 180.0:
                    rejected += 1
                    continue
                if throttle < 0 or throttle > 100.0:
                    throttle = max(0.0, min(100.0, throttle))

                # Clock continuity check
                if last_ts != -1:
                    if ts == last_ts:
                        duplicates += 1
                    elif ts < last_ts:
                        clock_resets += 1
                        anomalies.append(f"Row {total}: Clock reset ({ts} < {last_ts})")

                last_ts = ts
                valid_records.append({
                    "timestamp_us": ts,
                    "speed_kmh": speed,
                    "engine_rpm": rpm,
                    "engine_temp_c": temp,
                    "steering_angle_deg": steering,
                    "throttle_percent": throttle,
                    "accel_x_g": ax,
                    "accel_y_g": ay,
                    "ttc_seconds": float(row["ttc_seconds"]) if "ttc_seconds" in row and row["ttc_seconds"] else None,
                    "warning_level": row.get("warning_level", "SAFE"),
                })
            except Exception as e:
                rejected += 1
                anomalies.append(f"Row {total}: Format parse error ({e})")

        duration_s = 0.0
        if len(valid_records) >= 2:
            duration_s = (valid_records[-1]["timestamp_us"] - valid_records[0]["timestamp_us"]) / 1_000_000.0

        missing_pct = round((rejected / total * 100.0) if total > 0 else 0.0, 2)

        report = DataQualityReport(
            total_records=total,
            valid_records=len(valid_records),
            rejected_records=rejected,
            duplicate_timestamps=duplicates,
            clock_resets=clock_resets,
            missing_data_pct=missing_pct,
            duration_seconds=duration_s,
            laps_identified=0,  # Will be populated by lap detection engine
            checksum_sha256=sha256_hash,
            anomalies=anomalies[:10],  # Top 10 sample anomalies
        )

        return valid_records, report

    def parse_binary_stream(self, data: bytes) -> Tuple[List[DecodedTelemetryPacket], DataQualityReport]:
        """Parse raw continuous 16-byte binary frame stream from MicroSD card."""
        sha256_hash = hashlib.sha256(data).hexdigest()
        total_packets = len(data) // PacketDecoder.PACKET_SIZE
        valid_packets = []
        rejected = 0
        anomalies = []

        for i in range(total_packets):
            chunk = data[i * PacketDecoder.PACKET_SIZE : (i + 1) * PacketDecoder.PACKET_SIZE]
            try:
                pkt = PacketDecoder.decode(chunk)
                if not pkt.is_valid_checksum:
                    rejected += 1
                    anomalies.append(f"Packet {i}: Checksum error")
                    continue
                valid_packets.append(pkt)
            except Exception as e:
                rejected += 1
                anomalies.append(f"Packet {i}: Decode error ({e})")

        duration_s = 0.0
        if len(valid_packets) >= 2:
            duration_s = (valid_packets[-1].timestamp_ms - valid_packets[0].timestamp_ms) / 1000.0

        report = DataQualityReport(
            total_records=total_packets,
            valid_records=len(valid_packets),
            rejected_records=rejected,
            duplicate_timestamps=0,
            clock_resets=0,
            missing_data_pct=round((rejected / total_packets * 100.0) if total_packets > 0 else 0.0, 2),
            duration_seconds=duration_s,
            laps_identified=0,
            checksum_sha256=sha256_hash,
            anomalies=anomalies[:10],
        )

        return valid_packets, report
