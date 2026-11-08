// === Kurukshetra Kart Domain Types ===

export interface VehicleConfig {
  id: string;
  vehicle_id: string;
  name: string;
  drag_coefficient_cd: number;
  frontal_area_m2: number;
  rolling_resistance_crr: number;
  engine_power_kw: number;
  max_rpm: number;
  gear_ratio: number;
  created_at: string;
}

export interface Vehicle {
  id: string;
  name: string;
  chassis_code: string;
  engine_type: string;
  dry_mass_kg: number;
  wheelbase_m: number;
  track_width_m: number;
  created_at: string;
  configurations?: VehicleConfig[];
}

export interface Driver {
  id: string;
  name: string;
  racing_number: number;
  weight_kg: number;
  experience_level: string;
  created_at: string;
}

export interface TrackSector {
  id: string;
  track_id: string;
  sector_number: number;
  start_distance_m: number;
  end_distance_m: number;
  is_corner: boolean;
  corner_radius_m: number | null;
  corner_direction: string | null;
}

export interface Track {
  id: string;
  name: string;
  location: string | null;
  length_meters: number;
  num_turns: number;
  surface_type: string;
  centerline_geometry: string | null;
  created_at: string;
  sectors?: TrackSector[];
}

export interface WeatherCondition {
  id: string;
  session_id: string;
  ambient_temp_c: number;
  track_temp_c: number | null;
  relative_humidity_pct: number;
  barometric_pressure_hpa: number;
  air_density_kgm3: number;
  track_condition: string;
}

export interface Lap {
  id: string;
  session_id: string;
  lap_number: number;
  lap_time_s: number;
  sector_1_time_s: number | null;
  sector_2_time_s: number | null;
  sector_3_time_s: number | null;
  max_speed_kmh: number;
  min_speed_kmh: number;
  avg_rpm: number;
  max_lateral_g: number;
  is_valid: boolean;
}

export interface Session {
  id: string;
  name: string;
  date: string;
  track_id: string;
  driver_id: string;
  vehicle_id: string;
  vehicle_config_id: string;
  status: 'ACTIVE' | 'COMPLETED' | 'ABORTED';
  total_laps: number;
  best_lap_time_s: number | null;
  avg_lap_time_s: number | null;
  created_at: string;
  weather?: WeatherCondition;
  laps?: Lap[];
}

export interface TelemetryPoint {
  timestamp_us: number;
  speed_kmh: number;
  engine_rpm: number;
  engine_temp_c: number;
  steering_angle_deg: number;
  throttle_percent: number;
  accel_x_g: number;
  accel_y_g: number;
  accel_z_g?: number | null;
  gyro_z_degps?: number | null;
  obstacle_distance_cm?: number | null;
  closing_speed_mps?: number | null;
  ttc_seconds?: number | null;
  warning_level: 'SAFE' | 'CAUTION' | 'DANGER';
  sensor_status?: string | null;
}

export type ConnectionStatus = 'connected' | 'reconnecting' | 'disconnected';
export type WarningLevel = 'SAFE' | 'CAUTION' | 'DANGER';

