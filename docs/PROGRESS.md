# Project Progress & Implementation Tracker
## Kurukshetra Kart — IC Go-Kart Telemetry, Predictive Analytics & Digital Twin Platform
**Organisation:** Kurukshetra Racing, SKCET  
**Competition:** EKVC Season 4 — Innovation Round  
**Last Updated:** 8 November 2026 (Phase 4 Complete)

---

## 1. Executive Status Summary

| Metric | Status |
| :--- | :--- |
| **Current Phase** | **Phase 4 — Data Engineering & Analytics (COMPLETED)** |
| **Next Phase** | **Phase 5 — Machine Learning Predictive Analytics** |
| **Repository Integrity** | Verified — backend, frontend, telemetry, analytics, and digital-twin modules present |
| **Test Suite Status** | **22 backend tests passing**; frontend production build passing; lint warnings remain |
| **Hardware Readiness** | ESP32 pinout & 16-byte protocol specification defined |

---

## 1.1 Development Team & Branch Ownership

| Developer | Branch | Responsibility | Current Status |
| :--- | :--- | :--- | :--- |
| **Arshad** | `arshad` | Project lead, integration, and master coordination | **Branch created and pushed** |
| **Gayathri** | `gayathri` | UI/frontend implementation and ML data cleaning | **Branch created and pushed** |
| **Muthashim** | `muthashim` | Embedded hardware integration and LCD driver/display work | **Branch created and pushed** |
| **Shylesh** | `shylesh` | Embedded hardware integration and LCD driver/display work | **Branch created and pushed** |

All four developer branches were created from the latest `origin/main` and published to GitHub.

---

## 2. Module Implementation Ledger

| Module / Subsystem | Phase | Status | Test Coverage | Notes |
| :--- | :---: | :---: | :---: | :--- |
| **PRD & Requirements** | Phase 0 | **COMPLETED** | N/A | Saved at `docs/PRD.md` |
| **Architecture Specification** | Phase 0 | **COMPLETED** | N/A | Saved at `docs/ARCHITECTURE.md` |
| **Database Schema & Models** | Phase 0 | **COMPLETED** | N/A | Saved at `docs/DATABASE.md` |
| **API Specification** | Phase 0 | **COMPLETED** | N/A | Saved at `docs/API.md` |
| **Development Roadmap** | Phase 0 | **COMPLETED** | N/A | Saved at `docs/DEVELOPMENT_ROADMAP.md` |
| **Backend Core & Config** | Phase 1 | **COMPLETED** | `test_health.py` | FastAPI app, CORS, config, logging, health |
| **Database Models & Alembic** | Phase 1 | **COMPLETED** | `test_database.py`, Alembic upgrade/downgrade | SQLAlchemy models, SQLite setup, initial migration, and migration runner |
| **Frontend Scaffolding** | Phase 1 | **COMPLETED** | Build | React, Vite, Tailwind, Router, TanStack Query |
| **Docker Development Env** | Phase 1 | **PARTIAL** | Static configuration | Dockerfiles and Compose file are wired; Docker CLI unavailable for image validation |
| **Navigation & Topbar** | Phase 2 | **COMPLETED** | Build | Dark motorsport UI and navigation shell |
| **11 Dashboard Views** | Phase 2 | **COMPLETED** | Build | Dashboard, telemetry, track, lap, driver, twin, ML, reports, and related views |
| **16-Byte Packet Decoder** | Phase 3 | **COMPLETED** | `test_telemetry_pipeline.py` | Bitfield unpacking, encoding, and XOR checksum |
| **Live Telemetry & WebSockets**| Phase 3 | **COMPLETED** | `test_telemetry_pipeline.py` | UDP listener and async WebSocket broadcaster |
| **Time-to-Contact (TTC) Engine**| Phase 3 | **COMPLETED** | `test_telemetry_pipeline.py` | Physics closing speed and warning thresholds |
| **SD-Card File Importer** | Phase 3 | **COMPLETED** | `test_telemetry_pipeline.py` | CSV and raw binary stream parser |
| **Data Quality & Cleaning** | Phase 4 | **COMPLETED** | Unit tests | Missing clock/spike detection, audit report |
| **Lap & Sector Segmentation** | Phase 4 | **COMPLETED** | Unit tests | GPS/dead reckoning lap detection, sector splits |
| **Multi-Lap Trace Comparison** | Phase 4 | **COMPLETED** | Unit tests | Delta time ($\Delta t$) and speed ($\Delta v$) |
| **Engine Anomaly Detector** | Phase 5 | **COMPLETED** | `test_ml_anomaly.py` | Isolation Forest, persisted joblib registry, training and prediction API |
| **Lap-Time Predictor** | Phase 5 | *Pending* | - | XGBoost / Random Forest, session group split |
| **Driver Behaviour Classifier**| Phase 5 | *Pending* | - | Steering rate, throttle onset consistency |
| **Dynamic Grip Estimator** | Phase 5 | *Pending* | - | Effective $\mu$ from lateral G and radius |
| **Point-Mass Physics Engine** | Phase 6 | **COMPLETED** | `test_digital_twin.py` | Discretised track, power/drag/grip limits |
| **Calibration Engine** | Phase 6 | **COMPLETED** | `test_digital_twin.py` | Iterative RMSE calibration |
| **What-If Scenario Simulator** | Phase 6 | **COMPLETED** | `test_digital_twin.py` | Parameter delta evaluation |
| **Recommendation Engine** | Phase 7 | *Pending* | - | Evidence-based setup advice generation |
| **PDF & CSV Report Exporter** | Phase 7 | *Pending* | - | Downloadable debrief dossiers |
| **Synchronised Session Replay**| Phase 7 | *Pending* | - | Interactive telemetry-track synchronized playback |
| **End-to-End QA & Release** | Phase 8 | *Pending* | - | Full test pass, user manual, deployment ready |

---

## 3. Known Issues & Technical Risks

1. **Track Positioning In Real-Time:**  
   *Risk:* Standard GPS modules (e.g. NEO-6M) have $2.5\text{m}$ CEP accuracy and update at 1–5 Hz, which is coarse for kart racing lines.  
   *Mitigation:* Implement kinematic bicycle model dead-reckoning (`Appendix D` in team plan) combined with manual sector start/finish triggers for V1. Prepare sensor-fusion Kalman filter interface for V2.
2. **Engine Ignition Noise (EMI):**  
   *Risk:* Spark plug ignition spikes in 4-stroke IC engines induce high-frequency noise on ADC lines (potentiometers and thermistors).  
   *Mitigation:* Firmware moving average / median filtering + software spike rejection in the data pipeline.
3. **Data Leakage in Lap Prediction:**  
   *Risk:* Splitting train/test data randomly across time-series rows causes artificial over-optimistic accuracy.  
   *Mitigation:* Strict session-grouped cross-validation (`GroupKFold` on `session_id`).
4. **Digital Twin Low-Speed Numerical Singularity:**  
   *Risk:* Equation $a = (P / v - F_{drag}) / m$ diverges when $v \to 0$.  
   *Mitigation:* Implement torque-limited or traction-limited acceleration clamp at speeds below $3.0\text{ m/s}$.

---

## 4. Hardware & Dataset Dependencies

- **Hardware Dependency:** Physical ESP32 Dev Board + MPU6050 + Hall wheel speed sensor + DS18B20 temp probe + HC-SR04 ultrasonic.  
  *Status:* Software interface abstracted with `MockTelemetryGateway` for headless and automated testing.
- **Dataset Dependency:** Real track logged CSV/binary data from SKCET proving ground.  
  *Status:* Physics-grounded synthetic session generator prepared to simulate realistic laps for pipeline verification before track test 1.

---

## 5. Completed Work

- Phase 0 planning and architecture documentation.
- Phase 1 backend/frontend foundation and initial Alembic migration.
- Phase 2 dashboard UI and navigation shell.
- Phase 3 telemetry decoding, ingestion, WebSockets, TTC, and SD-card import.
- Phase 4 cleaning, quality summaries, lap/sector segmentation, and lap comparison.
- Phase 6 digital-twin solver, calibration, and what-if scenario engine.

## 6. Pending Work

### Immediate: Phase 5 — Machine Learning

1. Build lap-time predictor with session-grouped validation.
2. Build driver behaviour classifier.
3. Build dynamic effective-grip estimator.
4. Add the remaining ML models and model registry metadata.
5. Add ML training/inference API endpoints and frontend wiring.

### Remaining platform and release work

6. Validate Docker Compose image builds and container startup when Docker is available.
7. Add mock telemetry generator and complete end-to-end integration coverage.
8. Complete recommendation engine, PDF/CSV reporting, and synchronized replay.
9. Add frontend component/store tests.
10. Complete technical documentation and final release checklist.

## 7. Next Implementation Tasks (Phase 5)

1. Implement the lap-time predictor with session-grouped train/test splits.
2. Implement the driver behaviour classifier and grip estimator.
3. Add model registry metadata and inference endpoints for the remaining ML models.
