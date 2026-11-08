# Prioritised Implementation Backlog
## Kurukshetra Kart — IC Go-Kart Telemetry, Predictive Analytics & Digital Twin Platform
**Organisation:** Kurukshetra Racing, SKCET  
**Competition:** EKVC Season 4 — Innovation Round  
**Version:** 1.0.0  
**Date:** November 2026  

---

## Priority Scale Definition
- **P0 (Critical / Foundation):** Essential to the core loop (measure → ingest → validate → simulate).
- **P1 (High / Important):** Key analytical, visualization, and predictive features required for full demonstration.
- **P2 (Medium / Advanced):** Enhancements, stretch goals, and advanced modeling.
- **P3 (Low / Future):** Post-competition R&D (e.g. multi-body dynamics, RTK-GPS fusion).

---

## Epics & Work Breakdown

### Epic 1: Software Foundation (Phase 1)
- [x] **TASK-001 (P0):** Inspect existing repository and formulate architecture specifications.
- [ ] **TASK-002 (P0):** Initialize Python backend package structure (`backend/app/`).
- [ ] **TASK-003 (P0):** Define SQLAlchemy 2.0 database models for all 22 entities in `docs/DATABASE.md`.
- [ ] **TASK-004 (P0):** Set up SQLite database connection and Alembic migration harness.
- [ ] **TASK-005 (P0):** Scaffold React + TypeScript + Vite frontend (`frontend/`).
- [ ] **TASK-006 (P0):** Configure Tailwind CSS with dark engineering theme & Lucide icons.
- [ ] **TASK-007 (P0):** Create `.env.example`, `docker-compose.yml`, and `Dockerfile` specifications.
- [ ] **TASK-008 (P0):** Author automated health checks and database connectivity unit tests.

### Epic 2: Core Engineering Dashboard (Phase 2)
- [ ] **TASK-009 (P0):** Build responsive layout shell with navigation sidebar and telemetry status bar.
- [ ] **TASK-010 (P0):** Implement Overview Dashboard with key metrics and live state badges.
- [ ] **TASK-011 (P0):** Implement Live Telemetry view with digital gauges and dynamic sparklines.
- [ ] **TASK-012 (P1):** Implement Track Map view with circuit SVG projection and position indicator.
- [ ] **TASK-013 (P1):** Implement Lap Analysis view with multi-lap selection and sector times.
- [ ] **TASK-014 (P1):** Implement Driver Analysis view for throttle/steering consistency traces.
- [ ] **TASK-015 (P1):** Implement Engine Health view with thermal and RPM anomaly alerts.
- [ ] **TASK-016 (P1):** Implement Machine Learning Centre view for model metrics and versioning.
- [ ] **TASK-017 (P0):** Implement Digital Twin view with configuration controls and simulation graphs.
- [ ] **TASK-018 (P1):** Implement What-If Analysis view for parameter sweeps ($\Delta m, \Delta \mu$).
- [ ] **TASK-019 (P1):** Implement Session History view with upload modal and dataset status.
- [ ] **TASK-020 (P1):** Implement Reports view with export triggers (PDF/CSV).

### Epic 3: Telemetry Ingestion & Real-Time Gateway (Phase 3)
- [ ] **TASK-021 (P0):** Implement `PacketDecoder` for 16-byte binary protocol with checksum validation.
- [ ] **TASK-022 (P0):** Implement UDP socket ingestion listener and asynchronous packet buffer.
- [ ] **TASK-023 (P0):** Implement `/ws/v1/telemetry/{session_id}` WebSocket broadcasting manager.
- [ ] **TASK-024 (P0):** Implement Time-to-Contact (TTC) algorithm with Safe/Caution/Danger alerting.
- [ ] **TASK-025 (P0):** Implement SD-card file import parser for CSV and raw binary logs.
- [ ] **TASK-026 (P0):** Implement Mock Telemetry Generator simulating realistic track runs for testing.

### Epic 4: Data Engineering Pipeline & Analytics (Phase 4)
- [x] **TASK-027 (P0):** Build telemetry data cleaning pipeline (spike rejection, clock alignment).
- [x] **TASK-028 (P0):** Implement Data Quality Summary generator (completeness, noise ratio).
- [x] **TASK-029 (P0):** Implement Lap Detection engine (GPS threshold & dead-reckoning support).
- [x] **TASK-030 (P0):** Implement Sector Segmentation calculating min/max speeds and sector times.
- [x] **TASK-031 (P1):** Implement multi-lap delta comparison engine ($\Delta v$, $\Delta t$).

### Epic 5: Machine Learning Predictive Analytics (Phase 5)
- [ ] **TASK-032 (P0):** Feature engineering pipeline for session and sector aggregations.
- [ ] **TASK-033 (P0):** Implement Model 1: Engine Anomaly Detector (Isolation Forest).
- [ ] **TASK-034 (P0):** Implement Model 2: Lap-Time Predictor (Random Forest & XGBoost).
- [ ] **TASK-035 (P1):** Implement Model 3: Driver Behaviour Classifier.
- [ ] **TASK-036 (P1):** Implement Model 4: Dynamic Effective Grip Estimator.
- [ ] **TASK-037 (P0):** Model registry with metadata manifests and versioned joblib persistence.
- [ ] **TASK-038 (P0):** Fast inference API endpoints (`/api/v1/ml/predict`).

### Epic 6: Digital Twin Physics Engine & What-If Simulation (Phase 6)
- [ ] **TASK-039 (P0):** Track discretisation model (straights and corners with radii $R$).
- [ ] **TASK-040 (P0):** Kart vehicle model (mass, drag $C_d \cdot A$, power curve, gear ratio).
- [ ] **TASK-041 (P0):** Forward point-mass vehicle dynamics numerical integrator.
- [ ] **TASK-042 (P0):** Low-speed asymptotic singularity stabilization ($v \to 0$).
- [ ] **TASK-043 (P0):** Iterative model calibration loop against measured corner speeds (target RMSE $<5\%$).
- [ ] **TASK-044 (P0):** What-If Scenario Engine with parameter delta evaluation.

### Epic 7: Performance Analytics, Recommendations & Reporting (Phase 7)
- [ ] **TASK-045 (P0):** Rule-and-evidence setup recommendation engine.
- [ ] **TASK-046 (P0):** Automated PDF engineering session report generator.
- [ ] **TASK-047 (P0):** Telemetry CSV export package builder.
- [ ] **TASK-048 (P1):** Trackside session replay with synchronized position tracking.

### Epic 8: End-to-End Verification & Release (Phase 8)
- [ ] **TASK-049 (P0):** Pytest backend test suite covering all modules.
- [ ] **TASK-050 (P0):** Vitest frontend component and store test suite.
- [ ] **TASK-051 (P0):** End-to-end integration test of the complete closed feedback loop.
- [ ] **TASK-052 (P0):** Complete technical documentation (`TELEMETRY_PROTOCOL.md`, `USER_MANUAL.md`).
