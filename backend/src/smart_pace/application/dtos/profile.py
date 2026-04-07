from __future__ import annotations

from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from smart_pace.domain.enums import SportType


class CreateAthleteProfileInput(BaseModel):
    model_config = ConfigDict(frozen=True)

    user_id: UUID
    sport_type: SportType
    date_of_birth: date
    resting_heart_rate: int
    maximum_heart_rate: int
    functional_threshold_power: int | None = None
    current_vo2max: float | None = None
    training_experience_years: int = 0
    weekly_target_hours: float = 0.0


class UpdateHeartRateDataInput(BaseModel):
    model_config = ConfigDict(frozen=True)

    athlete_profile_id: UUID
    user_id: UUID
    resting_heart_rate: int
    maximum_heart_rate: int


class ViewHeartRateZonesInput(BaseModel):
    model_config = ConfigDict(frozen=True)

    athlete_profile_id: UUID
    user_id: UUID


class HeartRateZoneOutput(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str
    min_bpm: int
    max_bpm: int


class AthleteProfileOutput(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: UUID
    user_id: UUID
    sport_type: SportType
    date_of_birth: date
    resting_heart_rate: int
    maximum_heart_rate: int
    functional_threshold_power: int | None
    current_vo2max: float | None
    training_experience_years: int
    weekly_target_hours: float
    heart_rate_zones: list[HeartRateZoneOutput]
