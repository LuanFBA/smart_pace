from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from smart_pace.domain.value_objects.distance import Distance


@dataclass(frozen=True)
class Vo2max:
    """VO2max em ml/kg/min."""

    value: float

    def __post_init__(self) -> None:
        if self.value <= 0:
            raise ValueError("VO2max must be positive")

    @classmethod
    def estimate_from_cooper_test(cls, distance: Distance) -> Vo2max:
        """Estima VO2max pelo teste de Cooper (12 minutos).

        Fórmula: VO2max = (distância_metros - 504.9) / 44.73
        """
        result = (distance.meters - 504.9) / 44.73
        if result <= 0:
            raise ValueError("Distance too short to estimate VO2max from Cooper test")
        return cls(value=round(result, 1))
