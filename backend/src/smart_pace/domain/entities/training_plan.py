from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from uuid import UUID, uuid4

from smart_pace.domain.enums import SportType, TrainingPlanStatus
from smart_pace.domain.exceptions import InvalidDataException


@dataclass
class TrainingPlan:
    athlete_profile_id: UUID
    name: str
    goal_description: str
    start_date: date
    end_date: date
    sport_type: SportType
    id: UUID = field(default_factory=uuid4)
    status: TrainingPlanStatus = TrainingPlanStatus.DRAFT

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise InvalidDataException("Training plan name cannot be empty")
        if self.end_date <= self.start_date:
            raise InvalidDataException("end_date must be after start_date")

    def activate(self) -> None:
        if self.status != TrainingPlanStatus.DRAFT:
            raise InvalidDataException(
                f"Cannot activate plan with status '{self.status.value}'"
            )
        self.status = TrainingPlanStatus.ACTIVE

    def complete(self) -> None:
        if self.status != TrainingPlanStatus.ACTIVE:
            raise InvalidDataException(
                f"Cannot complete plan with status '{self.status.value}'"
            )
        self.status = TrainingPlanStatus.COMPLETED

    def cancel(self) -> None:
        if self.status in (TrainingPlanStatus.COMPLETED, TrainingPlanStatus.CANCELLED):
            raise InvalidDataException(
                f"Cannot cancel plan with status '{self.status.value}'"
            )
        self.status = TrainingPlanStatus.CANCELLED

    def duration_in_weeks(self) -> int:
        delta = self.end_date - self.start_date
        return delta.days // 7
