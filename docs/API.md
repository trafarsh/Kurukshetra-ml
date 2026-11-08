# REST & WebSocket API Specification
## Kurukshetra Kart — IC Go-Kart Telemetry, Predictive Analytics & Digital Twin Platform
**Organisation:** Kurukshetra Racing, SKCET  
**Competition:** EKVC Season 4 — Innovation Round  
**API Version:** v1  
**Base Path:** `/api/v1`  
**WebSocket Base:** `/ws/v1`  
**Document Version:** 1.0.0  
**Status:** Approved for Implementation  
**Date:** November 2026  

---

## 1. General Principles & Standards

1. **RESTful Architecture:** Standard HTTP verbs (`GET`, `POST`, `PUT`, `DELETE`) with meaningful HTTP status codes (`200 OK`, `201 Created`, `400 Bad Request`, `401 Unauthorized`, `403 Forbidden`, `404 Not Found`, `422 Unprocessable Entity`).
2. **Data Serialization:** Standard JSON serialization using snake_case property keys.
3. **Authentication:** Bearer token authentication with JSON Web Tokens (JWT) passed in the `Authorization: Bearer <token>` header.
4. **Error Handling:** Standardized error response envelope:
```json
{
  "error": {
    "code": "ENTITY_NOT_FOUND",
    "message": "Vehicle with id 'veh_01' does not exist.",
    "details": {}
  }
}
```

---

## 2. Authentication & User Endpoints

### 2.1 Authenticate User
- **Method & Path:** `POST /api/v1/auth/login`
- **Access:** Public
- **Request Body:**
```json
{
  "username": "admin",
  "password": "SecurePassword123!"
}
```
- **Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsIn...",
  "token_type": "bearer",
  "expires_in": 86400,
  "user": {
    "id": "usr_99",
    "username": "admin",
    "email": "admin@kurukshetraracing.skcet.ac.in",
    "role": "ADMIN"
  }
}
```

### 2.2 Get Current User Identity
- **Method & Path:** `GET /api/v1/auth/me`
- **Access:** Authenticated (Any Role)
- **Response (200 OK):** User object matching token subject.

---

## 3. Vehicle Endpoints

### 3.1 List Vehicles
- **Method & Path:** `GET /api/v1/vehicles`
- **Access:** Authenticated
- **Response (200 OK):**
```json
[
  {
    "id": "veh_01",
    "name": "Kurukshetra IC-04",
    "chassis_code": "SKCET-EKVC-2026",
    "engine_type": "125cc 4-Stroke IC Engine",
    "dry_mass_kg": 115.0,
    "wheelbase_m": 1.04,
    "track_width_m": 1.12,
    "created_at": "2026-11-08T10:00:00Z"
  }
]
```

### 3.2 Register Vehicle
- **Method & Path:** `POST /api/v1/vehicles`
- **Access:** Admin
- **Request Body:** Vehicle registration attributes.
- **Response (201 Created):** Created vehicle object.

### 3.3 Get Vehicle by ID
- **Method & Path:** `GET /api/v1/vehicles/{id}`
- **Response (200 OK):** Vehicle details with attached configurations.

### 3.4 Update Vehicle Configuration
- **Method & Path:** `PUT /api/v1/vehicles/{id}`
- **Access:** Admin, Vehicle Dynamics Engineer
- **Request Body:** Partial update fields.
- **Response (200 OK):** Updated vehicle object.

---

## 4. Driver Endpoints

### 4.1 List Drivers
- **Method & Path:** `GET /api/v1/drivers`
- **Response (200 OK):** Array of driver records.

### 4.2 Register Driver
- **Method & Path:** `POST /api/v1/drivers`
- **Access:** Admin
- **Request Body:**
```json
{
  "name": "Arshad Mohamed",
  "racing_number": 7,
  "weight_kg": 68.0,
  "experience_level": "COLLEGIATE_ADVANCED"
}
```
- **Response (201 Created):** Created driver object.

### 4.3 Get Driver Details
- **Method & Path:** `GET /api/v1/drivers/{id}`
- **Response (200 OK):** Driver profile with historical session count and personal best lap times.

---

## 5. Track Endpoints

### 5.1 List Tracks
- **Method & Path:** `GET /api/v1/tracks`
- **Response (200 OK):** Array of track layouts with sector splits and corner lists.

### 5.2 Register Track
- **Method & Path:** `POST /api/v1/tracks`
- **Access:** Admin, Vehicle Dynamics Engineer
- **Request Body:**
```json
{
  "name": "SKCET Innovation Proving Ground",
  "location": "Coimbatore, Tamil Nadu",
  "length_meters": 850.0,
  "num_turns": 9,
  "surface_type": "ASPHALT",
  "sectors": [
    {"sector_number": 1, "start_distance_m": 0.0, "end_distance_m": 280.0, "is_corner": false},
    {"sector_number": 2, "start_distance_m": 280.0, "end_distance_m": 590.0, "is_corner": true, "corner_radius_m": 18.5, "corner_direction": "RIGHT"},
    {"sector_number": 3, "start_distance_m": 590.0, "end_distance_m": 850.0, "is_corner": true, "corner_radius_m": 24.0, "corner_direction": "LEFT"}
  ]
}
```
- **Response (201 Created):** Created track record.

### 5.3 Get Track Details
- **Method & Path:** `GET /api/v1/tracks/{id}`
- **Response (200 OK):** Complete track geometry, sectors, and historical reference records.

---

## 6. Session Endpoints

### 6.1 List Sessions
- **Method & Path:** `GET /api/v1/sessions`
- **Query Params:** `track_id`, `driver_id`, `status`, `limit`, `offset`.
- **Response (200 OK):** Paginated session list with summary metrics.

### 6.2 Create Telemetry Session
- **Method & Path:** `POST /api/v1/sessions`
- **Access:** Telemetry Engineer, Admin
- **Request Body:**
```json
{
  "name": "Practice Stint 1 — Baseline Setup",
  "track_id": "trk_skcet_01",
  "driver_id": "drv_07",
  "vehicle_id": "veh_01",
  "vehicle_config_id": "cfg_base_01",
  "weather": {
    "ambient_temp_c": 32.0,
    "relative_humidity_pct": 58.0,
    "barometric_pressure_hpa": 1012.0,
    "track_condition": "DRY"
  }
}
```
- **Response (201 Created):** Session object with `status: ACTIVE`.

### 6.3 Get Session Details
- **Method & Path:** `GET /api/v1/sessions/{id}`
- **Response (200 OK):** Complete session overview including laps, weather, vehicle parameters, and telemetry status.

### 6.4 Finalize Session
- **Method & Path:** `POST /api/v1/sessions/{id}/finalize`
- **Access:** Telemetry Engineer, Admin
- **Response (200 OK):** Updates `status` to `COMPLETED`, computes final average and best lap times, triggers post-run summary.

---

## 7. Telemetry Ingestion Endpoints

### 7.1 Ingest Live Single / Batch Telemetry Packet
- **Method & Path:** `POST /api/v1/telemetry/ingest`
- **Access:** Hardware Gateway / System
- **Request Body (JSON or 16-Byte Binary base64):**
```json
{
  "session_id": "sess_01",
  "timestamp_us": 142850000,
  "speed_kmh": 62.4,
  "engine_rpm": 7800,
  "engine_temp_c": 91.5,
  "steering_angle_deg": -8.4,
  "throttle_percent": 90.0,
  "accel_x_g": 0.38,
  "accel_y_g": -0.92,
  "obstacle_distance_cm": 420.0,
  "closing_speed_mps": 3.2,
  "ttc_seconds": 1.31,
  "warning_level": "CAUTION"
}
```
- **Response (200 OK):** `{"status": "ACCEPTED", "packet_id": 14092}`.

### 7.2 Import Raw SD-Card Telemetry File
- **Method & Path:** `POST /api/v1/telemetry/import`
- **Access:** Data Engineer, Telemetry Engineer
- **Request:** `multipart/form-data` with fields `session_id`, `format` (`CSV` or `BINARY_16B`), and `file`.
- **Response (202 Accepted):**
```json
{
  "file_id": "file_sd_091",
  "session_id": "sess_01",
  "records_parsed": 142500,
  "duration_seconds": 1425.0,
  "data_quality": {
    "missing_timestamp_count": 0,
    "duplicate_timestamp_count": 0,
    "rejected_spike_count": 4,
    "completeness_score": 0.9997
  },
  "laps_detected": 12
}
```

### 7.3 Get Session Telemetry Stream / Traces
- **Method & Path:** `GET /api/v1/telemetry/{session_id}`
- **Query Params:** `lap_number`, `downsample_factor`, `from_us`, `to_us`.
- **Response (200 OK):** Array of telemetry point arrays optimized for charting.

### 7.4 Get Telemetry Summary
- **Method & Path:** `GET /api/v1/telemetry/{session_id}/summary`
- **Response (200 OK):** Peak speed, max RPM, thermal statistics, average G-forces, and warning frequency summary.

---

## 8. Analytics & Lap Comparison Endpoints

### 8.1 Get Session Analytics
- **Method & Path:** `GET /api/v1/analytics/{session_id}`
- **Response (200 OK):** Driving consistency index, braking stability metrics, and tire slip estimations.

### 8.2 Get Lap Breakdown
- **Method & Path:** `GET /api/v1/analytics/{session_id}/laps`
- **Response (200 OK):** Detailed lap time list, theoretical best lap (combining best sectors S1 + S2 + S3).

### 8.3 Get Sector Analysis
- **Method & Path:** `GET /api/v1/analytics/{session_id}/sectors`
- **Response (200 OK):** Min/max speed per sector, corner apex speeds, and throttle pickup distance.

### 8.4 Multi-Lap Telemetry Comparison
- **Method & Path:** `POST /api/v1/analytics/compare`
- **Request Body:**
```json
{
  "reference_lap_id": "lap_02",
  "comparison_lap_id": "lap_05",
  "channels": ["speed_kmh", "throttle_percent", "steering_angle_deg", "accel_y_g"]
}
```
- **Response (200 OK):** Time-aligned and distance-aligned delta traces: $\Delta \text{Speed}$, $\Delta \text{Time}$, and corner apex speed deltas.

---

## 9. Machine Learning Endpoints

### 9.1 List Model Registry
- **Method & Path:** `GET /api/v1/ml/models`
- **Response (200 OK):** Available models, active deployment versions, and training manifests.

### 9.2 Train Model
- **Method & Path:** `POST /api/v1/ml/train`
- **Access:** ML Engineer, Admin
- **Request Body:**
```json
{
  "model_type": "ENGINE_ANOMALY",
  "session_ids": ["sess_01", "sess_02"],
  "hyperparameters": {
    "n_estimators": 100,
    "contamination": 0.05,
    "random_state": 42
  }
}
```
- **Response (202 Accepted):** Model experiment ID, training progress status, and dataset validation stats.

### 9.3 Execute Model Inference
- **Method & Path:** `POST /api/v1/ml/predict`
- **Request Body:**
```json
{
  "model_type": "LAP_TIME_PREDICTION",
  "features": {
    "avg_speed_kmh": 68.2,
    "max_speed_kmh": 84.5,
    "min_corner_speed_kmh": 38.0,
    "avg_rpm": 7250,
    "full_throttle_pct": 64.0
  }
}
```
- **Response (200 OK):**
```json
{
  "prediction": 44.82,
  "confidence_interval": [44.20, 45.44],
  "model_version": "v1.1.0",
  "feature_importance": {
    "min_corner_speed_kmh": 0.42,
    "full_throttle_pct": 0.31,
    "max_speed_kmh": 0.18
  }
}
```

### 9.4 List Experiments & Metrics
- **Method & Path:** `GET /api/v1/ml/experiments` & `GET /api/v1/ml/metrics`
- **Response (200 OK):** Cross-validation scores (MAE, RMSE, $R^2$, F1) and ROC curves.

---

## 10. Digital Twin & Physics Simulation Endpoints

### 10.1 Manage Configurations
- **Method & Path:** `GET /api/v1/digital-twin/configurations` & `POST /api/v1/digital-twin/configurations`
- **Access:** Vehicle Dynamics Engineer, Admin
- **Payload:** Mass, tire grip $\mu$, drag $C_d \cdot A$, rolling resistance $C_{rr}$, power curve.

### 10.2 Calibrate Digital Twin Against Telemetry
- **Method & Path:** `POST /api/v1/digital-twin/calibrate`
- **Request Body:**
```json
{
  "session_id": "sess_01",
  "reference_lap_number": 3,
  "initial_grip_mu": 1.15,
  "convergence_tolerance": 0.05
}
```
- **Response (200 OK):**
```json
{
  "status": "CONVERGED",
  "initial_rmse_kmh": 6.8,
  "calibrated_grip_mu": 1.28,
  "final_rmse_kmh": 2.1,
  "error_percentage": 3.8,
  "iterations": 4
}
```

### 10.3 Run Forward Physics Simulation
- **Method & Path:** `POST /api/v1/digital-twin/simulate`
- **Request Body:** Configuration parameters + Track ID.
- **Response (200 OK):** Simulated lap time, maximum achievable speed, distance-indexed speed trace $v(s)$, and acceleration envelope.

---

## 11. What-If Scenario Endpoints

### 11.1 Create & Run What-If Scenario
- **Method & Path:** `POST /api/v1/scenarios`
- **Request Body:**
```json
{
  "name": "Mass Reduction -5kg + Softer Compound Grip +10%",
  "baseline_config_id": "dt_cfg_01",
  "parameter_deltas": {
    "delta_mass_kg": -5.0,
    "delta_grip_mu": 0.12,
    "delta_power_kw": 0.0
  }
}
```
- **Response (201 Created):** Simulated comparison metrics with `is_simulated: true`.

### 11.2 Compare Scenarios
- **Method & Path:** `POST /api/v1/scenarios/compare`
- **Request Body:** Array of scenario IDs.
- **Response (200 OK):** Side-by-side delta table and overlaid speed profiles.

---

## 12. Engineering Reporting Endpoints

### 12.1 Generate Engineering Report
- **Method & Path:** `POST /api/v1/reports/generate`
- **Request Body:** `{"session_id": "sess_01", "report_type": "SESSION_DEBRIEF"}`.
- **Response (201 Created):** Report ID and status.

### 12.2 Download Report
- **Method & Path:** `GET /api/v1/reports/{id}/download?format=pdf` (or `csv`)
- **Response:** Raw binary file stream (`application/pdf` or `text/csv`).

---

## 13. Real-Time WebSocket Interface

- **URI:** `ws://<host>:<port>/ws/v1/telemetry/{session_id}`
- **Client Handshake:** Automatically joins room for `session_id`.
- **Server Messages:**
  - `telemetry_update`: Live sensor measurements (10–20 Hz).
  - `ttc_alert`: Instant collision hazard update ($<50$ ms).
  - `session_status`: Changes in session state (Active / Completed).
- **Client Messages:**
  - `{"action": "ping"}` -> Server responds with `{"action": "pong", "timestamp": ...}`.

