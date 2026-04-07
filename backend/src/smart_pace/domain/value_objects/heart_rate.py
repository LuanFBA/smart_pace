from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class HeartRate:
    """Frequência cardíaca em batimentos por minuto."""

    beats_per_minute: int

    def __post_init__(self) -> None:
        if self.beats_per_minute <= 0:
            raise ValueError("Heart rate must be positive")


@dataclass(frozen=True)
class HeartRateZone:
    """Zona de frequência cardíaca para treino."""

    name: str
    min_bpm: int
    max_bpm: int

    def __post_init__(self) -> None:
        if self.min_bpm < 0:
            raise ValueError("min_bpm cannot be negative")
        if self.max_bpm <= self.min_bpm:
            raise ValueError("max_bpm must be greater than min_bpm")

    def contains(self, heart_rate: HeartRate) -> bool:
        """Verifica se um valor de FC está dentro desta zona."""
        return self.min_bpm <= heart_rate.beats_per_minute <= self.max_bpm
