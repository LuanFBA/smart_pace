from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Distance:
    """Distância em metros."""

    meters: int

    def __post_init__(self) -> None:
        if self.meters < 0:
            raise ValueError("Distance cannot be negative")

    @classmethod
    def from_kilometers(cls, kilometers: float) -> Distance:
        return cls(meters=round(kilometers * 1000))

    def to_kilometers(self) -> float:
        return self.meters / 1000
