"""Modelos Pydantic que representam os corpos das requisições HTTP."""

from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel

from smart_pace.domain.enums import SessionType, SportType


class CreateAthleteProfileRequest(BaseModel):
    sport_type: SportType
    date_of_birth: date
    resting_heart_rate: int
    maximum_heart_rate: int
    functional_threshold_power: int | None = None
    current_vo2max: float | None = None
    training_experience_years: int = 0
    weekly_target_hours: float = 0.0


class UpdateHeartRateRequest(BaseModel):
    resting_heart_rate: int
    maximum_heart_rate: int


class CreateTrainingPlanRequest(BaseModel):
    athlete_profile_id: UUID
    name: str
    goal_description: str
    start_date: date
    end_date: date
    sport_type: SportType


class ScheduleWorkoutSessionRequest(BaseModel):
    athlete_profile_id: UUID
    scheduled_date: date
    session_type: SessionType
    target_distance_meters: int | None = None
    target_duration_seconds: int | None = None
    target_min_pace_seconds_per_km: int | None = None
    target_max_pace_seconds_per_km: int | None = None


class LogWorkoutRequest(BaseModel):
    workout_session_id: UUID
    athlete_profile_id: UUID
    started_at: datetime
    finished_at: datetime
    actual_distance_meters: int
    actual_duration_seconds: int
    average_heart_rate: int | None = None
    maximum_heart_rate: int | None = None
    perceived_exertion: int | None = None
    notes: str | None = None
    average_power_watts: int | None = None


class UpdateWorkoutLogRequest(BaseModel):
    started_at: datetime
    finished_at: datetime
    actual_distance_meters: int
    actual_duration_seconds: int
    average_heart_rate: int | None = None
    maximum_heart_rate: int | None = None
    perceived_exertion: int | None = None
    notes: str | None = None
    average_power_watts: int | None = None
