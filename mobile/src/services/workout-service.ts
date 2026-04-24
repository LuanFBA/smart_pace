import { apiRequest } from "./api-client";
import type { WorkoutHistoryOutput, WorkoutLog, WorkoutSession, WorkoutSuggestion } from "../types/api";

export interface ScheduleSessionPayload {
  athlete_profile_id: string;
  scheduled_date: string; // YYYY-MM-DD
  session_type: string;
}

export interface LogWorkoutPayload {
  workout_session_id: string;
  athlete_profile_id: string;
  started_at: string;  // ISO datetime
  finished_at: string; // ISO datetime
  actual_distance_meters: number;
  actual_duration_seconds: number;
  average_heart_rate?: number | null;
  maximum_heart_rate?: number | null;
  perceived_exertion?: number | null;
  notes?: string | null;
  average_power_watts?: number | null;
}

export async function scheduleSession(
  data: ScheduleSessionPayload,
): Promise<WorkoutSession> {
  return apiRequest<WorkoutSession>("/workouts/sessions", {
    method: "POST",
    authenticated: true,
    body: JSON.stringify(data),
  });
}

export async function logWorkout(data: LogWorkoutPayload): Promise<WorkoutLog> {
  return apiRequest<WorkoutLog>("/workouts/log", {
    method: "POST",
    authenticated: true,
    body: JSON.stringify(data),
  });
}

export async function getSuggestion(
  athleteProfileId: string,
): Promise<WorkoutSuggestion> {
  const params = new URLSearchParams({ athlete_profile_id: athleteProfileId });
  return apiRequest<WorkoutSuggestion>(
    `/workouts/suggestion?${params.toString()}`,
    { authenticated: true },
  );
}

export async function getHistory(params: {
  athleteProfileId: string;
  limit?: number;
  offset?: number;
}): Promise<WorkoutHistoryOutput> {
  const searchParams = new URLSearchParams({
    athlete_profile_id: params.athleteProfileId,
    limit: String(params.limit ?? 5),
    offset: String(params.offset ?? 0),
  });
  return apiRequest<WorkoutHistoryOutput>(
    `/workouts/history?${searchParams.toString()}`,
    { authenticated: true },
  );
}
