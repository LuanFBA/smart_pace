import { apiRequest } from "./api-client";
import type { AthleteProfile, AuthTokens } from "../types/api";

export async function login(
  email: string,
  password: string,
): Promise<AuthTokens> {
  return apiRequest<AuthTokens>("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export async function register(
  email: string,
  password: string,
  fullName: string,
): Promise<AuthTokens> {
  return apiRequest<AuthTokens>("/auth/register", {
    method: "POST",
    body: JSON.stringify({ email, password, full_name: fullName }),
  });
}

export async function refreshToken(
  refresh_token: string,
): Promise<AuthTokens> {
  return apiRequest<AuthTokens>("/auth/token/refresh", {
    method: "POST",
    body: JSON.stringify({ refresh_token }),
  });
}

export async function getMyProfile(): Promise<AthleteProfile> {
  return apiRequest<AthleteProfile>("/profiles/me", {
    authenticated: true,
  });
}

export interface CreateProfilePayload {
  sport_type: "running" | "cycling";
  date_of_birth: string; // YYYY-MM-DD
  resting_heart_rate: number;
  maximum_heart_rate: number;
  functional_threshold_power?: number | null;
  current_vo2max?: number | null;
  training_experience_years: number;
  weekly_target_hours: number;
}

export async function createProfile(
  data: CreateProfilePayload,
): Promise<AthleteProfile> {
  return apiRequest<AthleteProfile>("/profiles/", {
    method: "POST",
    authenticated: true,
    body: JSON.stringify(data),
  });
}

export async function deleteAccount(): Promise<void> {
  return apiRequest<void>("/auth/account", {
    method: "DELETE",
    authenticated: true,
  });
}
