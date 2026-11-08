# Project Progress & Implementation Tracker
## Kurukshetra Kart — IC Go-Kart Telemetry, Predictive Analytics & Digital Twin Platform
**Organisation:** Kurukshetra Racing, SKCET  
**Competition:** EKVC Season 4 — Innovation Round  
**Last Updated:** November 2026 (Phase 0 Complete)  

---

## 1. Executive Status Summary

| Metric | Status |
| :--- | :--- |
| **Current Phase** | **Phase 0 — Planning & Architecture (COMPLETED)** |
| **Next Phase** | **Phase 1 — Software Foundation** |
| **Repository Integrity** | Verified — planning documents inspected, specs ground in hardware realities |
| **Test Suite Status** | Test harness scaffolding ready for Phase 1 |
| **Hardware Readiness** | ESP32 pinout & 16-byte protocol specification defined |

---

## 2. Module Implementation Ledger

| Module / Subsystem | Phase | Status | Test Coverage | Notes |
| :--- | :---: | :---: | :---: | :--- |
| **PRD & Requirements** | Phase 0 | **COMPLETED** | N/A | Saved at `docs/PRD.md` |
| **Architecture Specification** | Phase 0 | **COMPLETED** | N/A | Saved at `docs/ARCHITECTURE.md` |
| **Database Schema & Models** | Phase 0 | **COMPLETED** | N/A | Saved at `docs/DATABASE.md` |
| **API Specification** | Phase 0 | **COMPLETED** | N/A | Saved at `docs/API.md` |
| **Development Roadmap** | Phase 0 | **COMPLETED** | N/A | Saved at `docs/DEVELOPMENT_ROADMAP.md` |
| **Backend Core & Config** | Phase 1 | *Pending* | - | FastAPI app, CORS, logging, health |
| **Database Models & Alembic** | Phase 1 | *Pending* | - | SQLAlchemy 2.0 entities, SQLite migrations |
| **Frontend Scaffolding** | Phase 1 | *Pending* | - | React, Vite, Tailwind, Router, TanStack Query |
| **Docker Development Env** | Phase 1 | *Pending* | - | Dockerfile, docker-compose.yml |
| **Navigation & Topbar** | Phase 2 | *Pending* | - | Dark motorsport UI, connection status |
| **11 Dashboard Views** | Phase 2 | *Pending* | - | Overview, Live, Track, Lap, Driver, Twin, etc. |
| **16-Byte Packet Decoder** | Phase 3 | *Pending* | - | Bitfield unpacking, XOR checksum |
| **Live Telemetry & WebSockets**| Phase 3 | *Pending* | - | UDP listener, async WebSocket broadcaster |
| **Time-to-Contact (TTC) Engine**| Phase 3 | *Pending* | - | Physics closing speed & warning thresholds |
| **SD-Card File Importer** | Phase 3 | *Pending* | - | Multi-part upload, CSV/binary stream parser |
| **Data Quality & Cleaning** | Phase 4 | *Pending* | - | Missing clock/spike detection, audit report |
| **Lap & Sector Segmentation** | Phase 4 | *Pending* | - | GPS/dead reckoning lap detection, sector splits |
| **Multi-Lap Trace Comparison** | Phase 4 | *Pending* | - | Delta time ($\Delta t$) and speed ($\Delta v$) |
| **Engine Anomaly Detector** | Phase 5 | *Pending* | - | Isolation Forest, model serialization |
| **Lap-Time Predictor** | Phase 5 | *Pending* | - | XGBoost / Random Forest, session group split |
| **Driver Behaviour Classifier**| Phase 5 | *Pending* | - | Steering rate, throttle onset consistency |
| **Dynamic Grip Estimator** | Phase 5 | *Pending* | - | Effective $\mu$ from lateral G and radius |
| **Point-Mass Physics Engine** | Phase 6 | *Pending* | - | Discretised track, power/drag/grip limits |
| **Calibration Engine** | Phase 6 | *Pending* | - | Iterative RMSE tuning target $<5\%$ |
| **What-If Scenario Simulator** | Phase 6 | *Pending* | - | Parameter delta evaluation with isolated output |
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

## 5. Next Implementation Tasks (Phase 1)

1. Scaffolding backend directory layout: `backend/app/{api,core,models,schemas,repositories,services}`.
2. Implementing SQLAlchemy 2.0 models for all 22 entities in `backend/app/models/`.
3. Setting up SQLite database connection engine and migration runner.
4. Setting up FastAPI app with CORS middleware, structured logging, and `/health` route.
5. Scaffolding React + TypeScript + Vite frontend in `frontend/`.
6. Creating `docker-compose.yml` and testing backend/frontend startup.

