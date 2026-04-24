from __future__ import annotations

from datetime import UTC, datetime

from smart_pace.application.ports.clock import Clock


class SystemClock(Clock):
    """Implementação real do Clock usando datetime.now(UTC)."""

    def now(self) -> datetime:
        return datetime.now(UTC)
