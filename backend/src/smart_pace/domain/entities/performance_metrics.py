from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

from smart_pace.domain.exceptions import InvalidDataException
from smart_pace.domain.value_objects.heart_rate import HeartRateZone
from smart_pace.domain.value_objects.pace import Pace
from smart_pace.domain.value_objects.vo2max import Vo2max


@dataclass
class PerformanceMetrics:
    athlete_profile_id: UUID
    calculated_at: datetime
    estimated_vo2max: Vo2max
    heart_rate_zones: list[HeartRateZone]
    id: UUID = field(default_factory=uuid4)
    lactate_threshold_pace: Pace | None = None
    chronic_training_load: float = 0.0  # CTL (42 dias)
    acute_training_load: float = 0.0  # ATL (7 dias)

    def __post_init__(self) -> None:
        if self.chronic_training_load < 0:
            raise InvalidDataException("chronic_training_load cannot be negative")
        if self.acute_training_load < 0:
            raise InvalidDataException("acute_training_load cannot be negative")

    @property
    def training_stress_balance(self) -> float:
        """TSB = CTL - ATL. Positivo = descansado, negativo = fatigado."""
        return self.chronic_training_load - self.acute_training_load

    @property
    def fitness_fatigue_ratio(self) -> float | None:
        """Razão entre fitness (CTL) e fadiga (ATL). > 1 = descansado."""
        if self.acute_training_load == 0:
            return None
        return self.chronic_training_load / self.acute_training_load
