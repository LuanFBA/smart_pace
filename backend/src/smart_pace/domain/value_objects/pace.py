from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from smart_pace.domain.value_objects.distance import Distance
    from smart_pace.domain.value_objects.duration import Duration


@dataclass(frozen=True)
class Pace:
    """Ritmo de corrida/ciclismo em segundos por quilômetro."""

    seconds_per_kilometer: int

    def __post_init__(self) -> None:
        if self.seconds_per_kilometer <= 0:
            raise ValueError("Pace must be positive")

    @classmethod
    def from_distance_and_duration(
        cls,
        distance: Distance,
        duration: Duration,
    ) -> Pace:
        """Calcula o pace a partir de distância e duração."""
        if distance.meters <= 0:
            raise ValueError("Distance must be positive to calculate pace")
        seconds_per_km = round(duration.seconds * 1000 / distance.meters)
        return cls(seconds_per_kilometer=seconds_per_km)

    def to_min_km_string(self) -> str:
        """Formata como 'M:SS /km' (ex: '5:30')."""
        minutes = self.seconds_per_kilometer // 60
        seconds = self.seconds_per_kilometer % 60
        return f"{minutes}:{seconds:02d}"

    def is_faster_than(self, other: Pace) -> bool:
        """Pace menor = mais rápido."""
        return self.seconds_per_kilometer < other.seconds_per_kilometer

    def is_slower_than(self, other: Pace) -> bool:
        return self.seconds_per_kilometer > other.seconds_per_kilometer
