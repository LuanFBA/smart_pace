from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from smart_pace.domain.enums import SessionType


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
    started_at: datetime
    finished_at: datetime
    actual_distance_meters: int
    actual_duration_seconds: int
    average_pace_seconds_per_km: int
    average_heart_rate: int | None
    maximum_heart_rate: int | None
    perceived_exertion: int | None
    notes: str | None


class WorkoutHistoryOutput(BaseModel):
    model_config = ConfigDict(frozen=True)

    logs: list[WorkoutLogOutput]
    total_returned: int


class WorkoutSuggestionOutput(BaseModel):
    model_config = ConfigDict(frozen=True)

    suggested_session_type: SessionType
