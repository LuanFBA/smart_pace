from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4

from smart_pace.domain.enums import TrainingPhase
from smart_pace.domain.exceptions import InvalidDataException
from smart_pace.domain.value_objects.distance import Distance
from smart_pace.domain.value_objects.duration import Duration


@dataclass
class TrainingBlock:
    training_plan_id: UUID
    week_number: int
    phase: TrainingPhase
    target_weekly_distance: Distance
    target_weekly_duration: Duration
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        if self.week_number < 1:
            raise InvalidDataException("week_number must be at least 1")
