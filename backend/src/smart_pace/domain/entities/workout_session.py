from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from uuid import UUID, uuid4

from smart_pace.domain.enums import SessionStatus, SessionType
from smart_pace.domain.exceptions import InvalidDataException
from smart_pace.domain.value_objects.distance import Distance
from smart_pace.domain.value_objects.duration import Duration
from smart_pace.domain.value_objects.heart_rate import HeartRateZone
from smart_pace.domain.value_objects.pace import Pace


@dataclass
class WorkoutSession:
    athlete_profile_id: UUID
    scheduled_date: date
    session_type: SessionType
    id: UUID = field(default_factory=uuid4)
    training_block_id: UUID | None = None
    target_distance: Distance | None = None
    target_duration: Duration | None = None
    target_min_pace: Pace | None = None
    target_max_pace: Pace | None = None
    target_heart_rate_zone: HeartRateZone | None = None
    status: SessionStatus = SessionStatus.SCHEDULED

    def __post_init__(self) -> None:
        if self.target_min_pace and self.target_max_pace:
            # Pace menor = mais rápido, então min_pace deve ser o mais lento (maior valor)
            if (
                self.target_min_pace.seconds_per_kilometer
                > self.target_max_pace.seconds_per_kilometer
            ):
                raise InvalidDataException(
                    "target_min_pace must be faster (lower) than target_max_pace"
                )

    def mark_completed(self) -> None:
        self.status = SessionStatus.COMPLETED

    def mark_skipped(self) -> None:
        self.status = SessionStatus.SKIPPED

    def is_completed(self) -> bool:
        return self.status == SessionStatus.COMPLETED
