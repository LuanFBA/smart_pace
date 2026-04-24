from __future__ import annotations

from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from smart_pace.domain.enums import SportType, TrainingPlanStatus


class CreateTrainingPlanInput(BaseModel):
    model_config = ConfigDict(frozen=True)

    athlete_profile_id: UUID
    user_id: UUID
    name: str
    goal_description: str
    start_date: date
    end_date: date
    sport_type: SportType


class ActivateTrainingPlanInput(BaseModel):
    model_config = ConfigDict(frozen=True)

    plan_id: UUID
    user_id: UUID


class CancelTrainingPlanInput(BaseModel):
    model_config = ConfigDict(frozen=True)

    plan_id: UUID
    user_id: UUID


class ListTrainingPlansInput(BaseModel):
    model_config = ConfigDict(frozen=True)

    athlete_profile_id: UUID
    user_id: UUID


class GetTrainingPlanInput(BaseModel):
    model_config = ConfigDict(frozen=True)

    plan_id: UUID
    user_id: UUID


class TrainingPlanOutput(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: UUID
    athlete_profile_id: UUID
    name: str
    goal_description: str
    start_date: date
    end_date: date
    sport_type: SportType
    status: TrainingPlanStatus
    duration_in_weeks: int
