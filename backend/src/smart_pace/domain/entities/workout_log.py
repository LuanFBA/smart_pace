from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

from smart_pace.domain.exceptions import InvalidDataException
from smart_pace.domain.value_objects.distance import Distance
from smart_pace.domain.value_objects.duration import Duration
from smart_pace.domain.value_objects.heart_rate import HeartRate
from smart_pace.domain.value_objects.pace import Pace


@dataclass
class WorkoutLog:
    workout_session_id: UUID
    athlete_profile_id: UUID
    started_at: datetime
    finished_at: datetime
    actual_distance: Distance
    actual_duration: Duration
    average_pace: Pace
    id: UUID = field(default_factory=uuid4)
    average_heart_rate: HeartRate | None = None
    maximum_heart_rate: HeartRate | None = None
    perceived_exertion: int | None = None  # RPE 1-10
    notes: str | None = None
    average_power_watts: int | None = None  # Potência média — exclusivo para ciclismo

    def __post_init__(self) -> None:
        if self.finished_at <= self.started_at:
            raise InvalidDataException("finished_at must be after started_at")
        if self.perceived_exertion is not None:
            if not 1 <= self.perceived_exertion <= 10:
                raise InvalidDataException(
                    "perceived_exertion must be between 1 and 10"
                )
        if self.average_power_watts is not None and self.average_power_watts <= 0:
            raise InvalidDataException("average_power_watts must be positive")
        if self.average_heart_rate and self.maximum_heart_rate:
            if (
                self.average_heart_rate.beats_per_minute
                > self.maximum_heart_rate.beats_per_minute
            ):
                raise InvalidDataException(
                    "average_heart_rate cannot exceed maximum_heart_rate"
                )

    @classmethod
    def create_with_calculated_pace(
        cls,
        workout_session_id: UUID,
        athlete_profile_id: UUID,
        started_at: datetime,
        finished_at: datetime,
        actual_distance: Distance,
        actual_duration: Duration,
        **kwargs: object,
    ) -> WorkoutLog:
        """Cria um WorkoutLog calculando o pace automaticamente."""
        average_pace = Pace.from_distance_and_duration(actual_distance, actual_duration)
        return cls(
            workout_session_id=workout_session_id,
            athlete_profile_id=athlete_profile_id,
            started_at=started_at,
            finished_at=finished_at,
            actual_distance=actual_distance,
            actual_duration=actual_duration,
            average_pace=average_pace,
            **kwargs,  # type: ignore[arg-type]
        )

    def elapsed_time_seconds(self) -> int:
        """Tempo total decorrido (inclui pausas)."""
        return int((self.finished_at - self.started_at).total_seconds())
