from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ScheduleWorkoutSessionInput(BaseModel):
    model_config = ConfigDict(frozen=True)

    athlete_profile_id: UUID
    user_id: UUID
    scheduled_date: date
    session_type: str
    target_distance_meters: int | None = None
    target_duration_seconds: int | None = None
    target_min_pace_seconds_per_km: int | None = None
    target_max_pace_seconds_per_km: int | None = None


class WorkoutSessionOutput(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: UUID
    athlete_profile_id: UUID
    training_block_id: UUID | None
    scheduled_date: date
    session_type: str
    status: str
    target_distance_meters: int | None
    target_duration_seconds: int | None
    target_min_pace_seconds_per_km: int | None
    target_max_pace_seconds_per_km: int | None


class LogWorkoutInput(BaseModel):
    model_config = ConfigDict(frozen=True)

    workout_session_id: UUID
    athlete_profile_id: UUID
    user_id: UUID
    started_at: datetime
    finished_at: datetime
    actual_distance_meters: int
    actual_duration_seconds: int
    average_heart_rate: int | None = None
    maximum_heart_rate: int | None = None
    perceived_exertion: int | None = None
    notes: str | None = None
    average_power_watts: int | None = None


class ViewWorkoutHistoryInput(BaseModel):
    model_config = ConfigDict(frozen=True)

    athlete_profile_id: UUID
    user_id: UUID
    limit: int = 20
    offset: int = 0


class GetNextWorkoutSuggestionInput(BaseModel):
    model_config = ConfigDict(frozen=True)

    athlete_profile_id: UUID
    user_id: UUID


class WorkoutLogOutput(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: UUID
    workout_session_id: UUID
    athlete_profile_id: UUID
    session_type: str
    started_at: datetime
    finished_at: datetime
    actual_distance_meters: int
    actual_duration_seconds: int
    average_pace_seconds_per_km: int
    average_heart_rate: int | None
    maximum_heart_rate: int | None
    perceived_exertion: int | None
    notes: str | None
    average_power_watts: int | None


class WorkoutHistoryOutput(BaseModel):
    model_config = ConfigDict(frozen=True)

    logs: list[WorkoutLogOutput]
    total_returned: int
    total_count: int


class WorkoutSuggestionOutput(BaseModel):
    model_config = ConfigDict(frozen=True)

    suggested_session_type: str


class GetWorkoutLogInput(BaseModel):
    model_config = ConfigDict(frozen=True)

    log_id: UUID
    user_id: UUID


class UpdateWorkoutLogInput(BaseModel):
    model_config = ConfigDict(frozen=True)

    log_id: UUID
    user_id: UUID
    started_at: datetime
    finished_at: datetime
    actual_distance_meters: int
    actual_duration_seconds: int
    average_heart_rate: int | None = None
    maximum_heart_rate: int | None = None
    perceived_exertion: int | None = None
    notes: str | None = None
    average_power_watts: int | None = None


class DeleteWorkoutLogInput(BaseModel):
    model_config = ConfigDict(frozen=True)

    log_id: UUID
    user_id: UUID
