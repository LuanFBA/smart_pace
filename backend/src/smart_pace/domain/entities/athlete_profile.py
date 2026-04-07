from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from uuid import UUID, uuid4

from smart_pace.domain.enums import SportType
from smart_pace.domain.exceptions import InvalidDataException
from smart_pace.domain.value_objects.heart_rate import HeartRate
from smart_pace.domain.value_objects.vo2max import Vo2max


@dataclass
class AthleteProfile:
    user_id: UUID
    sport_type: SportType
    date_of_birth: date
    resting_heart_rate: HeartRate
    maximum_heart_rate: HeartRate
    id: UUID = field(default_factory=uuid4)
    functional_threshold_power: int | None = None  # watts, ciclismo
    current_vo2max: Vo2max | None = None
    training_experience_years: int = 0
    weekly_target_hours: float = 0.0

    def __post_init__(self) -> None:
        if (
            self.resting_heart_rate.beats_per_minute
            >= self.maximum_heart_rate.beats_per_minute
        ):
            raise InvalidDataException(
                "Resting heart rate must be lower than maximum heart rate"
            )
        if self.training_experience_years < 0:
            raise InvalidDataException("Training experience years cannot be negative")
        if self.weekly_target_hours < 0:
            raise InvalidDataException("Weekly target hours cannot be negative")

    def update_vo2max(self, vo2max: Vo2max) -> None:
        self.current_vo2max = vo2max

    def update_heart_rate(self, resting: HeartRate, maximum: HeartRate) -> None:
        """Atualiza frequência cardíaca com validação de invariante."""
        if resting.beats_per_minute >= maximum.beats_per_minute:
            raise InvalidDataException(
                "Resting heart rate must be lower than maximum heart rate"
            )
        self.resting_heart_rate = resting
        self.maximum_heart_rate = maximum

    def heart_rate_reserve(self) -> int:
        """Reserva de FC = FC máxima - FC de repouso (fórmula de Karvonen)."""
        return (
            self.maximum_heart_rate.beats_per_minute
            - self.resting_heart_rate.beats_per_minute
        )
