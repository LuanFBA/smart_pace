from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from smart_pace.application.dtos.profile import HeartRateZoneOutput


class ViewPerformanceDashboardInput(BaseModel):
    model_config = ConfigDict(frozen=True)

    athlete_profile_id: UUID
    user_id: UUID


class PerformanceDashboardOutput(BaseModel):
    model_config = ConfigDict(frozen=True)

    athlete_profile_id: UUID
    calculated_at: datetime | None
    estimated_vo2max: float | None
    heart_rate_zones: list[HeartRateZoneOutput]
    lactate_threshold_pace_seconds_per_km: int | None
    chronic_training_load: float
    acute_training_load: float
    training_stress_balance: float
    fitness_fatigue_ratio: float | None
