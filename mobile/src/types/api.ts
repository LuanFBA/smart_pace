// Tipos que espelham os DTOs do backend smart_pace

export type SportType = "running" | "cycling";

export type SessionType =
  | "easy_run"
  | "tempo"
  | "interval"
  | "long_run"
  | "recovery"
  | "cycling_endurance"
  | "cycling_interval";

export type SessionStatus = "scheduled" | "completed" | "skipped" | "partial";

// --- Auth ---

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

// --- Perfil de atleta ---

export interface HeartRateZone {
  name: string;
  min_bpm: number;
  max_bpm: number;
}

export interface AthleteProfile {
  id: string;
  user_id: string;
  user_full_name?: string;
  sport_type: SportType;
  date_of_birth: string;
  resting_heart_rate: number;
  maximum_heart_rate: number;
  functional_threshold_power: number | null;
  current_vo2max: number | null;
  training_experience_years: number;
  weekly_target_hours: number;
  heart_rate_zones: HeartRateZone[];
}

// --- Sessões de treino ---

export interface WorkoutSession {
  id: string;
  athlete_profile_id: string;
  training_block_id: string | null;
  scheduled_date: string;
  session_type: SessionType;
  status: SessionStatus;
  target_distance_meters: number | null;
  target_duration_seconds: number | null;
  target_min_pace_seconds_per_km: number | null;
  target_max_pace_seconds_per_km: number | null;
}

// --- Logs de treino ---

export interface WorkoutLog {
  id: string;
  workout_session_id: string;
  athlete_profile_id: string;
  session_type: SessionType;
  started_at: string;
  finished_at: string;
  actual_distance_meters: number;
  actual_duration_seconds: number;
  average_pace_seconds_per_km: number;
  average_heart_rate: number | null;
  maximum_heart_rate: number | null;
  perceived_exertion: number | null;
  notes: string | null;
  average_power_watts: number | null;
}

export interface WorkoutHistoryOutput {
  logs: WorkoutLog[];
  total_returned: number;
  total_count: number;
}

// --- Sugestão de treino ---

export interface WorkoutSuggestion {
  suggested_session_type: SessionType;
}

// --- Erros ---

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}
