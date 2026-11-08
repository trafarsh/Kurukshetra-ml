# System Architecture Document
## Kurukshetra Kart — IC Go-Kart Telemetry, Predictive Analytics & Digital Twin Platform
**Organisation:** Kurukshetra Racing, SKCET  
**Competition:** EKVC Season 4 — Innovation Round  
**Document Version:** 1.0.0  
**Status:** Approved for Implementation  
**Date:** November 2026  

---

## 1. High-Level Architecture Overview

Kurukshetra Kart is architected as a modular, decoupled, data-centric cyber-physical platform designed for motorsport engineering. It consists of nine distinct architectural tiers that establish an end-to-end feedback loop between physical kart operations and virtual simulation models.

```
                      +---------------------------------------+
                      |       PHYSICAL VEHICLE SENSORS        |
                      |  Wheel Speed | RPM | Temp | Steering   |
                      |  Throttle | IMU | Ultrasonic (TTC)     |
                      +-------------------+-------------------+
                                          |
                                          v
                      +---------------------------------------+
                      |         ESP32 ONBOARD FIRMWARE        |
                      |  Dual-Core FreeRTOS (Acquisition/DSP) |
                      +---------+-------------------+---------+
                                |                   |
                 10-20 Hz Radio |                   | 50-100 Hz
                (nRF24 / Wi-Fi) |                   | SPI / FAT32
                                v                   v
          +-----------------------+       +-------------------+
          |  GATEWAY / INGESTION  |       |  ONBOARD MICROSD  |
          |  UDP / Serial Receiver|       |  Raw Binary / CSV |
          +-----------+-----------+       +---------+---------+
                      |                             | Post-Session
                      v                             | Manual Upload
          +-----------------------+                 v
          |  TELEMETRY INGESTION  |<----------------+
          |  Packet Decoder & DSP |
          +-----------+-----------+
                      |
        +-------------+-------------+
        |                           |
        v                           v
+---------------+           +---------------+
|   WEBSOCKET   |           | DATA PIPELINE |
|  BROADCASTER  |           | Quality Check |
+-------+-------+           | Lap & Sector  |
        |                   +-------+-------+
        v                           |
+---------------+                   v
|   PIT-WALL    |           +---------------+
|   DASHBOARD   |           |  SQLITE / PG  |
|  (React + TS) |           |  STORE & RAWS |
+---------------+           +-------+-------+
                                    |
            +-----------------------+-----------------------+
            |                       |                       |
            v                       v                       v
    +---------------+       +---------------+       +---------------+
    |   ANALYTICS   |       |  ML INFERENCE |       | DIGITAL TWIN  |
    |  Lap & Sector |       | Anomaly / Lap |       | Physics Engine|
    |  Comparisons  |       | Driver / Grip |       | & Calibration |
    +-------+-------+       +-------+-------+       +-------+-------+
            |                       |                       |
            +-----------------------+-----------------------+
                                    |
                                    v
                            +---------------+
                            |   WHAT-IF     |
                            | RECOMMENDATION|
                            |   & REPORT    |
                            +---------------+
```

---

## 2. Subsystem Boundaries and Decoupling Principles

To ensure mission-critical stability during track operations, the platform enforces strict structural boundaries:

1. **Hardware Communication Decoupling:**  
   The ESP32 embedded firmware and the ground-station packet decoder operate independently from the application UI and database. If the telemetry database or machine learning service encounters high latency, the telemetry ingestion process remains unblocked.
2. **Dual-Path Data Redundancy:**  
   Wireless telemetry to the pit wall is an advisory monitoring feed. The definitive high-frequency dataset is continuously logged to the onboard MicroSD card. Telemetry loss or radio interference in corners has zero effect on post-run analysis.
3. **Simulation & ML Isolation:**  
   The physics-based Digital Twin engine is built as an independent computational core using NumPy and SciPy. It does not import FastAPI, database ORM models, or web frontend code. It can be run headless from CLI, notebooks, or API workers.
4. **Failure Domains:**  
   A failure or crash in an ML model inference job or a complex scenario simulation will never degrade live telemetry ingestion or interrupt driver Time-to-Contact (TTC) calculations.

---

## 3. Core Software Stack

### Frontend Application
- **Framework:** React 18 / 19 with TypeScript
- **Build System:** Vite
- **Styling:** Tailwind CSS with a custom motorsport dark engineering theme
- **Routing:** React Router v6
- **State & Caching:** TanStack Query (React Query) for API synchronization, Zustand for local telemetry buffer & UI state
- **Telemetry Visualisation:** Recharts & Canvas-based high-throughput sparklines
- **Geospatial & Track Layout:** Leaflet with custom SVG track geometry projection
- **Icons:** Lucide React

### Backend Core
- **Runtime:** Python 3.12+
- **Framework:** FastAPI (Asynchronous ASGI)
- **Data Validation & Schemas:** Pydantic v2
- **ORM & Data Access:** SQLAlchemy 2.0 (Async/Sync hybrid)
- **Database Migrations:** Alembic
- **Real-Time Gateway:** Python WebSockets & Asyncio UDP Server
- **Server:** Uvicorn with multi-worker support

### Data Engineering & Analytics
- **Array Computing & Numerics:** NumPy, SciPy
- **Tabular Data Processing:** Pandas, Polars (for high-speed batch file parsing)
- **Geospatial Processing:** Shapely

### Machine Learning
- **Anomaly Detection:** Scikit-learn (Isolation Forest)
- **Supervised Regression & Classification:** XGBoost, Scikit-learn (Random Forest, Gradient Boosting)
- **Model Serialization & Registry:** Joblib, Metadata JSON manifests

### Digital Twin Physics Engine
- **Vehicle Dynamics Model:** Point-mass kinematic & dynamic differential equations
- **Track Modelling:** Parametric centerline discretisation (segment lengths, curvature radii, banking, elevation)
- **Numerical Solvers:** Explicit Euler / Runge-Kutta numerical integration with low-speed asymptotic stabilization

---

## 4. Communication Protocols & Contracts

### 4.1 Live ESP32 16-Byte Telemetry Packet (V1 Standard)
The embedded system encodes a fixed 16-byte binary frame to maximize wireless throughput over 2.4 GHz RF / UDP:

| Byte Offset | Field Name | Data Type | Encoding / Units | Resolution / Range |
| :--- | :--- | :--- | :--- | :--- |
| `0..3` | `timestamp_ms` | `uint32_t` (4B) | Unsigned 32-bit LE int | Milliseconds since boot (wraps ~49 days) |
| `4..5` | `speed_raw` | `uint16_t` (2B) | Scaled unsigned int | Speed in km/h $\times 100$ ($0.00 - 655.35$ km/h) |
| `6..7` | `engine_rpm` | `uint16_t` (2B) | Unsigned int | Direct RPM ($0 - 20,000$ RPM) |
| `8` | `engine_temp_c`| `uint8_t` (1B) | Unsigned int | Temperature in $^\circ\text{C}$ ($0 - 255^\circ\text{C}$) |
| `9` | `steering_deg` | `int8_t` (1B) | Signed int | Steering angle in degrees ($-128^\circ \text{ to } +127^\circ$) |
| `10` | `throttle_pct` | `uint8_t` (1B) | Unsigned int | Throttle pedal travel ($0 - 100\%$) |
| `11` | `accel_x_raw` | `int8_t` (1B) | Scaled signed int | Longitudinal G $\times 50$ ($-2.56\text{g to } +2.54\text{g}$) |
| `12` | `accel_y_raw` | `int8_t` (1B) | Scaled signed int | Lateral G $\times 50$ ($-2.56\text{g to } +2.54\text{g}$) |
| `13..14`| `ttc_raw` | `uint16_t` (2B) | Scaled unsigned int | Time-to-contact in seconds $\times 100$ ($0.00 - 655.35$ s; $65535 = \infty$) |
| `15` | `flags_checksum`| `uint8_t` (1B) | Bitfield & Checksum | Bits 0..1: Warning Level, Bits 2..3: Sensor Flags, Bits 4..7: XOR Checksum |

### 4.2 WebSocket Live Stream Protocol
- **Endpoint:** `ws://<host>:<port>/ws/v1/telemetry/{session_id}`
- **Payload Format:** JSON text frame:
```json
{
  "type": "telemetry_update",
  "session_id": "sess_20261108_01",
  "timestamp_ms": 142850,
  "data": {
    "speed_kmh": 64.2,
    "engine_rpm": 7820,
    "engine_temp_c": 92,
    "steering_deg": -14.5,
    "throttle_pct": 85.0,
    "accel_x_g": 0.34,
    "accel_y_g": -1.18,
    "obstacle_distance_cm": 380,
    "closing_speed_mps": 4.2,
    "ttc_seconds": 0.90,
    "warning_level": "DANGER",
    "sensor_status": {
      "rpm": "OK",
      "temp": "OK",
      "imu": "OK",
      "distance": "OK"
    }
  }
}
```

---

## 5. Repository Directory Layout

The project follows a clean, maintainable monorepo layout:

```
kurukshetra-kart/
├── frontend/                     # React + TypeScript + Vite Pit Dashboard
│   ├── src/
│   │   ├── app/                  # Routing and global application providers
│   │   ├── components/           # Reusable UI widgets, gauges, charts, alerts
│   │   ├── layouts/              # Pit-wall navigation & engineering layout
│   │   ├── pages/                # 11 Dedicated views (Overview, Live, Track, etc.)
│   │   ├── features/             # Subsystem components (telemetry, ml, twin)
│   │   ├── hooks/                # WebSocket, query, and responsive hooks
│   │   ├── services/             # Axios API client bindings
│   │   ├── stores/               # Zustand state stores
│   │   └── types/                # TypeScript interface declarations
│   ├── public/                   # Static assets, branding, track SVGs
│   ├── package.json
│   └── vite.config.ts
│
├── backend/                      # Python FastAPI application
│   ├── app/
│   │   ├── api/routes/           # REST & WebSocket endpoints
│   │   ├── core/                 # Config, security, logging, exceptions
│   │   ├── models/               # SQLAlchemy ORM models
│   │   ├── schemas/              # Pydantic request/response schemas
│   │   ├── repositories/         # Database access abstraction
│   │   └── services/             # Business logic layer
│   ├── migrations/               # Alembic database migrations
│   └── tests/                    # Backend unit & integration tests
│
├── data-engineering/             # Pipeline, parsing, and quality engine
│   ├── ingestion/                # Binary & CSV stream decoders
│   ├── preprocessing/            # Filtering, interpolation, clock alignment
│   ├── analytics/                # Lap detection, sector segmentation, math
│   └── tests/                    # Pipeline validation tests
│
├── machine-learning/             # Dedicated ML package
│   ├── datasets/                 # Manifests and dataset preparation tools
│   ├── models/                   # IsolationForest, XGBoost, Classifiers
│   ├── training/                 # Model training routines & hyperparameter tuning
│   ├── evaluation/               # Metrics, confusion matrix, ROC calculation
│   ├── inference/                # Real-time and batch prediction services
│   ├── registry/                 # Persisted model weights and metadata
│   └── tests/                    # ML unit and reproducibility tests
│
├── digital-twin/                 # Independent physics simulation core
│   ├── track/                    # Track geometry & centerline discretisation
│   ├── vehicle/                  # Kart mass, power curve, drag, gear model
│   ├── environment/              # Air density, temperature, surface grip
│   ├── driver/                   # Driver input replay & profile modeller
│   ├── physics/                  # Point-mass solver & differential integrator
│   ├── calibration/              # Iterative grip parameter estimation loop
│   ├── scenarios/                # What-if parameter delta evaluation
│   └── tests/                    # Physics equation and convergence tests
│
├── embedded-interface/           # Hardware protocols and simulation adapters
│   ├── protocols/                # Binary packet specs & C-struct equivalents
│   ├── decoders/                 # Python and C++ decoder reference implementations
│   └── simulators/               # Hardware mock generator (sends live packets)
│
├── sample-data/                  # Verifiable real and synthetic test datasets
│   ├── synthetic/                # Labelled synthetic sessions for CI/CD
│   └── reference/                # Track layout coordinate matrices
│
├── reports/                      # Output directory for generated PDF & CSV reports
├── docs/                         # Specifications, architecture, guides, PRD
├── docker-compose.yml            # Multi-service local orchestrator
├── Dockerfile.backend            # Container specification for backend
├── Dockerfile.frontend           # Container specification for frontend
├── .env.example                  # Environment variable template
└── README.md                     # Getting started and setup guide
```

---

## 6. Security, Reliability & Operational Resilience

1. **Authentication & Authorization:**  
   Passkeys and session JWTs provide role separation (Admin vs Telemetry Engineer vs Driver). Critical operations (e.g. modifying track coordinates or vehicle dry weight) require Admin privileges.
2. **Input Validation:**  
   Every external input (UDP frame, uploaded file, REST payload) is strictly validated against Pydantic schemas. Corrupt frames are rejected with diagnostic logs.
3. **Data Protection:**  
   Original raw files uploaded from SD cards are stored in read-only directories with SHA-256 validation to prevent loss or silent modification.
4. **Resilient Streaming:**  
   The frontend WebSocket client implements exponential backoff reconnection with an on-screen visual connection indicator (Green: Connected, Yellow: Reconnecting, Red: Disconnected).

