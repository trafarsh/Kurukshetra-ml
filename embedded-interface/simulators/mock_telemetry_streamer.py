"""
Mock ESP32 Live Telemetry Packet Streamer.

Simulates physical go-kart sensor acquisition and broadcasts compact 16-byte binary
frames over UDP to the pit-wall receiver at 20 Hz (50 ms intervals).

Usage:
  python embedded-interface/simulators/mock_telemetry_streamer.py --host 127.0.0.1 --port 8888 --rate 20
"""
from __future__ import annotations

import argparse
import math
import socket
import sys
import time

# Ensure backend package can be imported
sys.path.insert(0, "./backend")

from app.telemetry.packet_decoder import PacketDecoder
from app.telemetry.ttc_engine import TTCEngine


def run_streamer(host: str = "127.0.0.1", port: int = 8888, rate_hz: float = 20.0):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    interval = 1.0 / rate_hz
    ttc_engine = TTCEngine()

    print(f"===========================================================")
    print(f" Kurukshetra Kart — ESP32 Telemetry Transmitter Simulator")
    print(f" Target Gateway: {host}:{port}")
    print(f" Transmission Rate: {rate_hz} Hz ({interval * 1000:.1f} ms period)")
    print(f" Packet Size: 16 Bytes (Binary Compact Frame)")
    print(f" Press Ctrl+C to stop.")
    print(f"===========================================================")

    start_time = time.time()
    packet_seq = 0

    try:
        while True:
            t = time.time() - start_time
            ts_ms = int(t * 1000)

            # Physics simulation for a typical 44s lap:
            # Main straight, Turn 1, Back straight, Hairpin
            lap_phase = (t % 44.0) / 44.0  # 0.0 to 1.0

            if lap_phase < 0.25:  # Main Straight: full power
                speed = 40.0 + 46.0 * (lap_phase / 0.25)
                throttle = 100.0
                rpm = int(5000 + 4200 * (lap_phase / 0.25))
                steering = 0.0 + 1.2 * math.sin(t * 3.0)
                ax = 0.65
                ay = 0.05
            elif lap_phase < 0.40:  # Turn 1 Braking & Apex
                progress = (lap_phase - 0.25) / 0.15
                speed = 86.0 - 44.0 * math.sin(progress * math.pi / 2)
                throttle = 0.0 if progress < 0.6 else 45.0
                rpm = max(3800, int(9200 - 4500 * progress))
                steering = -24.5 * math.sin(progress * math.pi)
                ax = -1.15
                ay = -1.22 * math.sin(progress * math.pi)
            elif lap_phase < 0.70:  # Sector 2 Sweepers
                speed = 55.0 + 20.0 * math.sin(t * 1.5)
                throttle = 75.0 + 20.0 * math.sin(t * 2.0)
                rpm = int(6200 + 1800 * math.sin(t * 1.5))
                steering = 18.0 * math.cos(t * 1.8)
                ax = 0.25 * math.cos(t * 1.5)
                ay = 0.95 * math.sin(t * 1.8)
            else:  # Final Straight & Turn 9
                speed = 70.0 + 14.0 * math.sin(t)
                throttle = 90.0
                rpm = int(7500 + 1200 * math.sin(t))
                steering = 5.0 * math.sin(t)
                ax = 0.35
                ay = 0.20

            # Thermal model: slow heat rise up to 92°C with throttle correlation
            temp = 75.0 + 18.0 * (1.0 - math.exp(-t / 120.0)) + 3.0 * (throttle / 100.0)

            # Ultrasonic distance & TTC simulation
            # Kart occasionally approaches simulated backmarker
            if 15.0 < (t % 30.0) < 20.0:
                dist_cm = max(20.0, 420.0 - (t % 30.0 - 15.0) * 80.0)
            else:
                dist_cm = 480.0

            ttc_res = ttc_engine.update(dist_cm, ts_ms * 1000)

            # Encode canonical 16-byte packet
            raw_packet = PacketDecoder.encode(
                timestamp_ms=ts_ms,
                speed_kmh=speed,
                engine_rpm=rpm,
                engine_temp_c=temp,
                steering_deg=steering,
                throttle_pct=throttle,
                accel_x_g=ax,
                accel_y_g=ay,
                ttc_seconds=ttc_res.ttc_seconds,
                warning_level=ttc_res.warning_level,
                sensor_fault=False,
            )

            sock.sendto(raw_packet, (host, port))
            packet_seq += 1

            if packet_seq % 40 == 0:  # Print every 2 seconds
                ttc_str = f"{ttc_res.ttc_seconds:.2f}s" if ttc_res.ttc_seconds else "None"
                print(
                    f"[{ts_ms:08d} ms] #{packet_seq:05d} | "
                    f"Speed: {speed:5.1f} km/h | RPM: {rpm:5d} | Temp: {temp:4.1f}°C | "
                    f"Steer: {steering:5.1f}° | Ax: {ax:5.2f}g | Ay: {ay:5.2f}g | "
                    f"TTC: {ttc_str:>6s} [{ttc_res.warning_level}]"
                )

            time.sleep(interval)

    except KeyboardInterrupt:
        print(f"\nTransmitter halted. Sent {packet_seq} frames.")
    finally:
        sock.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Mock ESP32 Telemetry Transmitter")
    parser.add_argument("--host", default="127.0.0.1", help="Target UDP host")
    parser.add_argument("--port", type=int, default=8888, help="Target UDP port")
    parser.add_argument("--rate", type=float, default=20.0, help="Transmission rate in Hz")
    args = parser.parse_args()

    run_streamer(args.host, args.port, args.rate)

