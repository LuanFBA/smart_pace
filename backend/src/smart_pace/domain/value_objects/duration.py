from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Duration:
    """Duração em segundos."""

    seconds: int

    def __post_init__(self) -> None:
        if self.seconds < 0:
            raise ValueError("Duration cannot be negative")

    @classmethod
    def from_hms(cls, hours: int, minutes: int, seconds: int) -> Duration:
        total = hours * 3600 + minutes * 60 + seconds
        return cls(seconds=total)

    def to_hms_string(self) -> str:
        """Formata como 'H:MM:SS' (ex: '1:23:45')."""
        hours = self.seconds // 3600
        remainder = self.seconds % 3600
        minutes = remainder // 60
        secs = remainder % 60
        if hours > 0:
            return f"{hours}:{minutes:02d}:{secs:02d}"
        return f"{minutes}:{secs:02d}"
