# Product Requirements Document (PRD)
## Kurukshetra Kart — IC Go-Kart Telemetry, Predictive Analytics & Digital Twin Platform
**Organisation:** Kurukshetra Racing, Sri Krishna College of Engineering and Technology (SKCET)  
**Competition:** EKVC Season 4 — Innovation Round  
**Document Version:** 1.0.0  
**Status:** Approved for Implementation  
**Date:** November 2026  

---

## 1. Product Summary

Kurukshetra Kart is an end-to-end motorsport telemetry, predictive analytics, and physics-calibrated digital twin platform engineered specifically for an Internal Combustion (IC) formula student / commercial go-kart.

The platform bridges real-world track testing and scientific simulation through a closed engineering feedback loop:
```
REAL KART
  → SENSOR ACQUISITION (ESP32, 9 Channels)
  → TELEMETRY (Dual-Path: SD-Card 100 Hz + Wireless 10–20 Hz)
  → DATA PIPELINE & QUALITY ENGINE
  → MACHINE LEARNING (Anomaly, Lap Time, Driver Behaviour, Grip)
  → DIGITAL TWIN (Physics Point-Mass & Track Model)
  → WHAT-IF SIMULATION SCENARIOS
  → PERFORMANCE ANALYTICS & SETUP RECOMMENDATIONS
  → REAL-WORLD TRACK VALIDATION
```

Rather than serving as an aesthetic dashboard, Kurukshetra Kart is a quantitative decision-support instrument that enables race engineers and drivers to validate simulation predictions against measured telemetry, measure Time-to-Contact (TTC) for driver collision awareness, and optimise chassis and powertrain configurations with quantifiable error margins.

---

## 2. Problem Statement

Go-kart racing teams in collegiate competitions such as EKVC face major technical and operational handicaps:
1. **Zero / Inadequate Real-Time Visibility:** Drivers operate without real-time thermal, dynamic, or closing-speed telemetry, leading to engine overheating, undetected mechanical faults, and on-track collisions.
2. **Unstructured Telemetry & Data Loss:** Sensor data is rarely timestamped against a common clock, resulting in cross-channel desynchronisation, corrupted SD writes, and inability to trace historic setups.
3. **Subjective Driver Feedback:** Lap analysis is based on anecdotal driver impressions rather than empirical brake-point, steering-rate, and throttle application traces.
4. **Absence of Calibrated Simulation:** Teams either rely on expensive, uncalibrated black-box commercial software or have no virtual test bench to assess the impact of mass, grip, or gear-ratio changes before taking to the track.
5. **Disconnected Engineering Feedback:** Setup adjustments (tire pressure, track width, gear ratio) are conducted by trial and error without comparing simulated expectations against measured delta.

---

## 3. Product Goals

The Kurukshetra Kart platform must:
1. **Acquire & Ingest Telemetry:** Capture 9 core physical sensor streams via ESP32, logging at 50–100 Hz to an onboard MicroSD card while streaming a 16-byte wireless telemetry packet at 10–20 Hz to a pit station.
2. **Driver Collision Awareness:** Compute real-time Time-to-Contact (TTC) from forward distance measurements, triggering Safe/Caution/Danger alerts on a steering-wheel OLED within 50 ms latency.
3. **Robust Data Pipeline:** Ingest raw binary or CSV files, validate timestamps, detect dropped frames/sensor spikes, segment laps and sectors, and output reproducible structured datasets.
4. **Machine Learning Predictive Analytics:**
   - Detect engine operating anomalies via Isolation Forests.
   - Predict lap times based on sector and vehicle dynamics features.
   - Classify driver cornering/braking behaviours into quantified styles.
   - Estimate dynamic tire grip coefficients ($\mu$).
5. **Physics-Calibrated Digital Twin:** Discretise track geometry and simulate a point-mass vehicle dynamics envelope (forward acceleration, braking limits, lateral grip constraints, aerodynamic drag, rolling resistance), executing an iterative calibration loop to achieve $<5\%$ corner-speed prediction error against measured data.
6. **What-If Scenario Simulation:** Evaluate parameter variations (vehicle mass, ambient temperature, engine power, tire grip) and output delta metrics without altering baseline telemetry.
7. **Evidence-Based Engineering Recommendations:** Generate setup recommendations directly linked to anomalous or sub-optimal telemetry observations.
8. **Export & Reporting:** Produce automated engineering PDF reports and structured CSV telemetry exports for trackside debriefs.

---

## 4. Non-Goals

To maintain strict engineering rigor, the following capabilities are explicitly declared outside the V1/V2 scope:
- **No Autonomous Vehicle Control:** The system will NOT actuate brakes, throttle, or steering. All TTC warnings are strictly advisory driver aids.
- **No Production-Grade Suspension / Multi-Body Simulation:** The physics engine uses a validated point-mass model; full multi-body kinematic suspension links, chassis torsion, and tire carcass thermal-deformation models are excluded.
- **No Camera-Based Vision Odometry:** Track positioning will rely on GPS / Dead Reckoning / Manual sector markers, not real-time computer vision SLAM.
- **No Black-Box ML Claims:** ML models will not claim knowledge of "driver intent" or "guaranteed lap time reduction"; all predictions include uncertainty bounds and model versioning.
- **No Ungrounded Fabrications:** If a sensor channel (e.g. brake pressure or oil pressure) is uninstalled on the kart, the UI and API will report `null` / `unavailable` and will never synthesize fake values.

---

## 5. Target Users & Role-Based Access Control (RBAC)

| Role | Responsibilities | Key Capabilities |
| :--- | :--- | :--- |
| **Administrator** | System operations, security, master assets | User management, kart/vehicle registration, track definitions, system config, global audit log access. |
| **Telemetry Engineer** | Real-time monitoring & trackside comms | Monitor live pit-wall telemetry, inspect sensor health, verify packet drop rate & wireless RSSI, acknowledge active warnings. |
| **Data Engineer** | Telemetry ingestion & data quality | Import SD card CSV/binary dumps, execute data cleaning pipeline, verify clock drift, inspect data quality reports. |
| **ML Engineer** | Model development & inference | Train anomaly detectors, lap-time predictors, driver classifiers; inspect confusion matrices, feature importances, and model registries. |
| **Vehicle Dynamics Engineer** | Simulation & Digital Twin calibration | Configure kart mass, Cd, engine power curve, track segment geometry; run physics simulator, calibrate tire grip, run what-if scenarios. |
| **Driver** | Performance review | View driving consistency, compare throttle/steering traces between laps, review sector deltas. |
| **Team Manager** | Executive performance review | Download comprehensive session reports, evaluate driver development, compare race stint pace and mechanical reliability. |

---

## 6. Functional Requirements

### 6.1 Telemetry Ingestion & Live Communication (TEL)
- **TEL-01 (P0): Compact 16-Byte Wireless Packet Decoding**  
  *Input:* Raw binary buffer from UDP socket / serial / RF receiver.  
  *Expected Output:* Validated `TelemetryPacket` schema (timestamp_us, speed_kmh, rpm, temp_c, steering_deg, throttle_pct, accel_x, accel_y, ttc_s, flags).  
  *Acceptance Criteria:* Decodes at up to 50 Hz with $<1$ ms processing time; checksum validation rejects corrupted frames; corrupted packets increment error counter without crashing service.  
  *Dependencies:* Backend telemetry decoder module.

- **TEL-02 (P0): WebSocket Telemetry Broadcast**  
  *Input:* Decoded live telemetry packet.  
  *Expected Output:* JSON broadcast on `/ws/v1/telemetry/{session_id}`.  
  *Acceptance Criteria:* Client receives state within 30 ms; handles client reconnection, heartbeat/ping-pong, and sets stale data flag if packet stream drops for $>1000$ ms.

- **TEL-03 (P0): Time-to-Contact (TTC) Real-Time Computation**  
  *Input:* Front distance ($d_{prev}, d_{curr}$) and $\Delta t$.  
  *Expected Output:* Closing speed $v_{close} = (d_{prev} - d_{curr}) / \Delta t$; $TTC = d_{curr} / v_{close}$ if $v_{close} > 0$, else $\infty$.  
  *Acceptance Criteria:* Evaluates warning zone (SAFE: $>2.5$ s, CAUTION: $1.0–2.5$ s, DANGER: $<1.0$ s). Latency from sensor sample to warning $<50$ ms.

- **TEL-04 (P0): SD-Card Raw Log Ingestion (CSV & Binary)**  
  *Input:* Multi-megabyte raw session log file uploaded via API.  
  *Expected Output:* Stored raw archive, validated record stream, parsing status report.  
  *Acceptance Criteria:* Parses 100,000 records in $<2$ seconds. Preserves original raw file intact on disk.

### 6.2 Data Engineering & Quality Pipeline (DAT)
- **DAT-01 (P0): Data Cleaning & Anomaly Filtering**  
  *Input:* Raw ingested telemetry records.  
  *Expected Output:* Cleaned, time-aligned Pandas/Polars DataFrame and Data Quality Summary.  
  *Acceptance Criteria:* Identifies duplicate timestamps, imputes micro-dropouts with linear interpolation, flags impossible sensor values (e.g., RPM $>16000$, Temp $>250^\circ\text{C}$), outputs reject counts and data completeness ratio.

- **DAT-02 (P0): Lap & Sector Segmentation**  
  *Input:* Continuous session telemetry + Track definition (or manual lap markers).  
  *Expected Output:* List of discrete `Lap` entities with split times, entry/exit speeds, and sector statistics.  
  *Acceptance Criteria:* Correctly identifies lap boundaries based on GPS coordinates or dead reckoning distance threshold; calculates lap time, sector 1/2/3 splits, min/max speed, and average RPM.

### 6.3 Machine Learning Pipeline (ML)
- **ML-01 (P0): Engine Anomaly Detection**  
  *Input:* Engine RPM, engine temperature, vehicle speed, longitudinal acceleration.  
  *Algorithm:* Isolation Forest.  
  *Expected Output:* Anomaly score $[-1.0, 1.0]$, binary classification (Normal / Anomalous), feature attribution.  
  *Acceptance Criteria:* Flags abnormal thermal-RPM spikes without false-positive alarms during normal pit idling or redline shifts. Evaluated on labelled synthetic/track test sets.

- **ML-02 (P0): Lap-Time Prediction**  
  *Input:* Sector speeds, max speed, min corner speed, throttle percentage distribution, mean lateral G.  
  *Algorithm:* Random Forest / XGBoost Regressor.  
  *Expected Output:* Predicted lap time (seconds), error vs actual, prediction interval.  
  *Acceptance Criteria:* Out-of-fold $R^2 \ge 0.85$, $MAE < 0.6$ seconds on test sessions. Train/test split partitioned strictly by session to avoid temporal data leakage.

- **ML-03 (P1): Driver Behaviour Classification**  
  *Input:* Steering angle velocity ($\dot{\delta}$), throttle onset rate ($d\text{Throttle}/dt$), longitudinal deceleration.  
  *Expected Output:* Driving style tags (Smooth vs Aggressive cornering, Progressive vs Sudden throttle).  
  *Acceptance Criteria:* Rule-grounded classifier with verifiable threshold boundaries documented in ML methodology.

- **ML-04 (P1): Effective Tire Grip ($\mu$) Estimation**  
  *Input:* Speed $v$, corner radius $R$, lateral acceleration $a_{lat}$.  
  *Expected Output:* Estimated instantaneous and peak grip coefficient $\mu = a_{lat} / g$.  
  *Acceptance Criteria:* Estimates effective tire grip envelope; filters out transient curb impacts.

### 6.4 Digital Twin & Physics Simulation (DTW)
- **DTW-01 (P0): Point-Mass Vehicle Dynamics Engine**  
  *Input:* Kart parameters (mass, engine power curve, drag $C_d \cdot A$, rolling resistance $C_{rr}$, tire grip $\mu$), track profile (straight lengths, corner radii).  
  *Expected Output:* Predicted speed trace $v(s)$, acceleration trace $a(s)$, sector times, total lap time.  
  *Acceptance Criteria:* Respects governing physics:
  $$a_{lat, max} = \mu g, \quad v_{corner, max} = \sqrt{\mu g R}, \quad F_{drag} = \frac{1}{2}\rho C_d A v^2, \quad a_{accel} = \frac{P_{eng}/v - F_{drag} - F_{rr}}{m}$$
  Numerical integration stable at low speeds ($v \to 0$ without zero-division).

- **DTW-02 (P0): Iterative Model Calibration Loop**  
  *Input:* Simulated lap speed trace vs Measured lap speed trace.  
  *Expected Output:* Parameter adjustments ($\Delta \mu, \Delta C_d$), Root-Mean-Square Error (RMSE) on corner speeds.  
  *Acceptance Criteria:* Calibrates $\mu$ to bring simulation corner speed error $<5\%$ against measured lap telemetry.

- **DTW-03 (P0): What-If Scenario Engine**  
  *Input:* Baseline configuration + parameter modifications ($\Delta m$, $\Delta P$, $\Delta \mu$, wet track flag).  
  *Expected Output:* Delta comparison: $\Delta \text{Lap Time}$, $\Delta \text{Top Speed}$, $\Delta \text{Sector Times}$, speed difference overlay.  
  *Acceptance Criteria:* Baseline configuration remains immutable; simulation results tagged clearly with `is_simulated: true`.

### 6.5 Performance Analytics & Recommendation Engine (REC)
- **REC-01 (P0): Structured Engineering Recommendations**  
  *Input:* Telemetry metrics, anomaly flags, driver behaviour classifications, simulation deltas.  
  *Expected Output:* Structured recommendation objects with `subsystem`, `observation`, `telemetry_evidence`, `suggested_action`, `expected_effect`, and `confidence`.  
  *Acceptance Criteria:* Every recommendation cites specific numerical evidence (e.g. "Corner 3 apex speed is 8 km/h below grip limit of 52 km/h due to early coasting").

### 6.6 Reporting & Export (REP)
- **REP-01 (P0): Automated PDF & CSV Session Reports**  
  *Input:* Session ID.  
  *Expected Output:* Downloadable formatted PDF summary and standard CSV telemetry package.  
  *Acceptance Criteria:* PDF contains track map, best lap comparison, engine thermal summary, ML anomaly log, digital twin calibration metrics, and engineering recommendations.

---

## 7. Non-Functional Requirements (NFR)

1. **Reliability & Fault Tolerance:** Local SD-card logging on the kart must operate independently of wireless link status. A drop in wireless communication or WebSocket disconnection must not halt telemetry acquisition or crash the server.
2. **Performance & Latency:**
   - Real-time packet decoding: $<2$ ms per packet.
   - Live WebSocket propagation: $<50$ ms end-to-end latency.
   - Dashboard UI rendering: 60 FPS under continuous 20 Hz telemetry streaming.
   - Batch data ingestion: $<3$ seconds for a 30-minute session log (180,000 records).
3. **Data Integrity:** Raw ingested files are immutable and stored in a dedicated raw storage volume. Checksums (CRC32/SHA256) verify data integrity across transfer boundaries.
4. **Security & Authentication:** Role-Based Access Control (RBAC) enforced via JWT bearer tokens. Passwords hashed using bcrypt. Sensitive credentials managed through environment variables.
5. **Observability & Logging:** Structured JSON logging on backend services with correlation IDs. Standardized health endpoints (`/health`, `/health/ready`).
6. **Reproducibility:** All ML models, training datasets, and digital twin simulation parameters are versioned and stored with execution hashes.

---

## 8. User Workflows

### Workflow 1: Kart Registration
1. Administrator navigates to **Vehicles** page.
2. Enters vehicle name, chassis ID, dry mass (kg), wheelbase (m), engine model, max RPM, gear ratio, drag coefficient, and frontal area.
3. System validates parameters and persists vehicle record.

### Workflow 2: Track & Driver Registration
1. Administrator creates Driver profile (name, license/tag, team role, weight).
2. Administrator creates Track profile (name, location, length, number of corners, sector division points, GPS bounds).

### Workflow 3: Live Telemetry Session
1. Telemetry Engineer initiates new Session on Pit Dashboard, linking Kart, Driver, Track, and Weather metadata.
2. Backend opens WebSocket server `/ws/v1/telemetry/{session_id}`.
3. ESP32 hardware begins transmitting 16-byte UDP packets to pit gateway.
4. Pit gateway ingests packets, validates checksum, decodes signals, and pushes updates via WebSockets.
5. Live dashboard gauges (Speed, RPM, Temperature, G-Force, TTC warning) update smoothly.

### Workflow 4: Post-Run SD-Card Ingestion & Data Cleaning
1. Data Engineer removes MicroSD card from kart after session, uploads `.bin` or `.csv` file via **Session History** upload modal.
2. Ingestion service stores raw copy in `data/raw/`.
3. Cleaning pipeline parses packets, verifies clock monotonically increases, handles dropouts, detects laps/sectors, and creates cleaned parquet/sqlite tables.
4. Data Quality Report is generated and presented in the UI.

### Workflow 5: Driver & Lap Performance Analysis
1. Driver and Race Engineer open **Lap Analysis** page.
2. Select Session and choose two laps (e.g. Lap 2 vs Lap 5) for comparison.
3. Interactive multi-signal charts display overlaid Speed traces, Throttle positions, Steering angles, and Lateral G.
4. System highlights delta time ($\Delta t$) across sectors and displays corner minimum speeds.

### Workflow 6: Digital Twin Simulation & Calibration
1. Dynamics Engineer opens **Digital Twin** workspace.
2. Selects real Session Lap 1 as reference baseline.
3. Simulator generates point-mass velocity profile along track geometry.
4. Calibration engine computes error between measured corner speeds and simulated corner speeds, adjusting effective grip coefficient $\mu$ until RMSE $<5\%$.
5. Calibration report is saved.

### Workflow 7: What-If Scenario Exploration
1. Dynamics Engineer creates Scenario: "Increase kart mass by 10 kg and reduce tire grip by $15\%$ (simulating wet track)".
2. Scenario engine executes simulation against calibrated track geometry.
3. UI displays baseline vs scenario speed trace, showing projected lap time loss ($+1.85$ s) and reduced corner apex speeds.

### Workflow 8: Engineering Report Generation
1. Team Manager clicks **Generate Session Report**.
2. Reporting service compiles session telemetry, lap deltas, ML anomaly logs, digital twin validation graphs, and setup recommendations into a branded PDF report.
3. Report is downloaded for competition judging debrief.

---

## 9. Product Acceptance Criteria

- [ ] **AC-01:** Complete monorepo builds and runs via Docker Compose with zero manual file hacking.
- [ ] **AC-02:** Backend exposes all `/api/v1/` endpoints with OpenAPI/Swagger documentation at `/docs`.
- [ ] **AC-03:** Live telemetry WebSocket streams at 10–20 Hz with simulated or hardware packets without memory leaks.
- [ ] **AC-04:** Raw SD-card CSV/binary upload processes with full data quality summary and lap segmentation.
- [ ] **AC-05:** TTC subsystem alerts correctly reflect SAFE ($>2.5$ s), CAUTION ($1.0–2.5$ s), and DANGER ($<1.0$ s) states.
- [ ] **AC-06:** All four ML models (Engine Anomaly, Lap Time Prediction, Driver Behaviour, Grip Estimation) have reproducible training and inference pipelines.
- [ ] **AC-07:** Digital twin physics engine correctly calculates lateral and longitudinal limits with calibration RMSE reporting.
- [ ] **AC-08:** What-if scenario comparison cleanly isolates simulated deltas from measured baseline data.
- [ ] **AC-09:** Comprehensive test suite passes with $>80\%$ code coverage across all core modules.

