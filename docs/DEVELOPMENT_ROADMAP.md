# Development Roadmap & Phase-Gate Specification

## Kurukshetra Kart — IC Go-Kart Telemetry, Predictive Analytics & Digital Twin Platform

**Organisation:** Kurukshetra Racing, SKCET
**Competition:** EKVC Season 4 — Innovation Round
**Document Version:** 1.0.0
**Status:** Approved for Implementation
**Date:** November 2026

---

## 1. Roadmap Overview & Phase-Gate Strategy

Development follows a strict phase-gated engineering methodology where no phase is marked complete without executable code, passing unit/integration tests, and verified documentation.

```
PHASE 0: Inspection & Planning (Complete)
   │
   ▼
PHASE 1: Software Foundation (Backend, Database, Frontend Scaffolding, Docker)
   │
   ▼
PHASE 2: Core Dashboard & UI Architecture (11 Dedicated Engineering Pages)
   │
   ▼
PHASE 3: Telemetry Ingestion & Protocols (16-Byte Packet Decoder, UDP, WebSockets, SD CSV)
   │
   ▼
PHASE 4: Data Engineering & Analytics Pipeline (Cleaning, Clock Alignment, Lap/Sector Analysis)
   │
   ▼
PHASE 5: Machine Learning Subsystem (Anomaly Detection, Lap Prediction, Driver Style, Grip)
   │
   ▼
PHASE 6: Digital Twin Physics Engine (Point-Mass Dynamics, Calibration Loop, What-If)
   │
   ▼
PHASE 7: Performance Analytics, Recommendations & Automated Reporting (PDF/CSV)
   │
   ▼
PHASE 8: End-to-End Testing, Validation & Release Packaging
```

---

## 2. Phase Breakdown & Deliverables

### PHASE 0 — Repository Inspection & Architecture Planning

- **Goal:** Audit existing files, extract hardware pinout & packet specs, formulate PRD, Architecture, Database schema, API specification, Roadmap, and Implementation Backlog.
- **Deliverables:**
  - `docs/PRD.md`
  - `docs/ARCHITECTURE.md`
  - `docs/DATABASE.md`
  - `docs/API.md`
  - `docs/DEVELOPMENT_ROADMAP.md`
  - `docs/PROGRESS.md`
- **Gate Criteria:** All 6 foundational documents authored, cross-verified against team project plans and competition goals.

---

### PHASE 1 — Software Foundation

- **Goal:** Establish runnable backend, database, and frontend skeletons with automated test harnesses.
- **Tasks:**
  1. Initialize Python FastAPI backend structure (`backend/app`).
  2. Implement SQLite/PostgreSQL database models with SQLAlchemy 2.0.
  3. Set up Alembic database migrations.
  4. Initialize React + TypeScript + Vite frontend (`frontend/`).
  5. Implement shared configuration (`.env.example`), logging, and `/health` endpoints.
  6. Create `docker-compose.yml` for unified development environment.
  7. Run initial backend test suite verifying database connection and health check endpoints.
- **Exit Criteria:** Frontend builds cleanly (`npm run build`); Backend starts via Uvicorn and returns `{"status": "HEALTHY"}` at `/health`; database tables migrate successfully.

---

### PHASE 2 — Core Engineering Dashboard

- **Goal:** Construct dark-theme motorsport workstation UI with navigation across all 11 core views.
- **Tasks:**
  1. Configure Tailwind CSS with high-contrast motorsport engineering theme (dark navy/charcoal, safety greens, caution ambers, danger reds).
  2. Build top bar with kart connection status, active session indicator, and navigation sidebar.
  3. Build 11 core page views:
     - Overview Dashboard
     - Live Telemetry
     - Track Map
     - Lap Analysis
     - Driver Analysis
     - Engine Health
     - Machine Learning Centre
     - Digital Twin
     - What-If Analysis
     - Session History
     - Reports
  4. Implement vehicle, driver, and track management modal dialogs and forms.
  5. Add realistic demo/fallback fixtures clearly labelled as simulated/development data.
- **Exit Criteria:** Seamless client-side routing across all 11 pages; zero console errors; responsive layout for trackside laptops and pit monitors.

---

### PHASE 3 — Telemetry Ingestion & Real-Time Communication

- **Goal:** Ingest live 16-byte binary packets and parse historical SD-card CSV logs.
- **Tasks:**
  1. Build Python `PacketDecoder` implementing the 16-byte binary protocol with checksum validation.
  2. Implement UDP socket listener and serial stream adapter for live telemetry.
  3. Implement `/ws/v1/telemetry/{session_id}` WebSocket broadcasting manager with connection tracking.
  4. Implement Time-to-Contact (TTC) algorithm with $<50$ ms latency and Safe/Caution/Danger thresholding.
  5. Implement multi-format SD card file importer (CSV and binary chunks) with raw storage backup.
  6. Connect frontend Zustand store and Recharts sparklines to the live WebSocket stream.
- **Exit Criteria:** Decoder unit tests achieve 100% pass on valid and malformed packets; live stream renders at 20 Hz without dropped frames or memory leaks.

---

### PHASE 4 — Data Engineering Pipeline & Analytics

- **Goal:** Transform raw, noisy telemetry logs into structured, time-aligned, lap-segmented datasets.
- **Tasks:**
  1. Implement data quality engine detecting clock drift, duplicate timestamps, and sensor spikes.
  2. Generate Data Quality Reports (completeness percentage, rejected outliers, dropouts).
  3. Build Lap Detection engine supporting GPS coordinates, dead reckoning, and manual markers.
  4. Build Sector Segmentation calculating sector 1/2/3 split times and min/max speeds.
  5. Build multi-lap trace comparison service (delta speed $\Delta v$, delta time $\Delta t$).
- **Exit Criteria:** End-to-end test processes raw 30-minute session dump into discrete lap records with verifiable data quality audit.

---

### PHASE 5 — Machine Learning Subsystem

- **Goal:** Deliver the 4 core predictive analytics models with isolated training, evaluation, and inference.
- **Tasks:**
  1. **Model 1: Engine Anomaly Detector** (Isolation Forest on RPM, Temp, Speed, Accel).
  2. **Model 2: Lap-Time Predictor** (Random Forest & XGBoost on sector features, group-split by session).
  3. **Model 3: Driver Behaviour Classifier** (Steering rate, throttle onset, braking consistency).
  4. **Model 4: Dynamic Grip Estimator** ($\mu = a_{lat} / g$ filtered by corner radius).
  5. Model registry with joblib persistence, version tracking, and inference APIs.
  6. Machine Learning Centre UI displaying model performance, confusion matrices, and feature importances.
- **Exit Criteria:** All models possess automated training scripts and unit tests; group-based validation ensures zero temporal data leakage; inference latency $<15$ ms.

---

### PHASE 6 — Physics-Based Digital Twin & What-If Simulation

- **Goal:** Discretise track geometry and simulate point-mass vehicle dynamics with empirical calibration.
- **Tasks:**
  1. Track Model: Discretise centerline into straights and corners with radii $R$.
  2. Kart Model: Mass $m$, drag $C_d \cdot A$, power curve $P(v)$, rolling resistance $C_{rr}$, grip limit $\mu$.
  3. Physics Engine: Numerical integration of longitudinal power-limited acceleration, braking constraints, and lateral grip limit ($v_{corner} = \sqrt{\mu g R}$).
  4. Calibration Engine: Compare simulated corner speeds against measured lap telemetry and iteratively adjust $\mu$ to achieve RMSE $<5\%$.
  5. What-If Scenario Engine: Allow engineers to simulate parameter variations ($\Delta m, \Delta P, \Delta \mu$) and display overlaid delta traces.
- **Exit Criteria:** Physics equations validated against analytical test cases; low-speed singularity handling verified; calibration loop converges in $<5$ iterations.

---

### PHASE 7 — Recommendations, Reporting & Session Replay

- **Goal:** Synthesise telemetry, ML predictions, and simulation insights into actionable engineering outputs.
- **Tasks:**
  1. Recommendation Engine: Rule-and-evidence generator that correlates telemetry observations with setup advice.
  2. Automated Report Generator: Build PDF generator (ReportLab/WeasyPrint) and CSV package exporter.
  3. Trackside Session Replay: Synchronised playback of lap telemetry with interactive track position marker.
- **Exit Criteria:** Generates production-ready, downloadable PDF debrief reports with charts, calibration metrics, and structured setup actions.

---

### PHASE 8 — End-to-End Validation & Release

- **Goal:** Comprehensive quality assurance, security hardening, and documentation finalisation.
- **Tasks:**
  1. Backend test suite (`pytest`) covering all endpoints, decoders, ML models, and physics solvers.
  2. Frontend test suite (`vitest`) verifying components and stores.
  3. Docker Compose end-to-end integration test.
  4. Author final technical documentation: `TELEMETRY_PROTOCOL.md`, `DIGITAL_TWIN.md`, `USER_MANUAL.md`.
  5. Verify EKVC Season 4 Innovation Round compliance checklist.
- **Exit Criteria:** All tests green; Docker container boots cleanly; demonstration workflow operable end-to-end.
