from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime


class Clock(ABC):
    """Abstração de relógio para permitir testes determinísticos."""

    @abstractmethod
    def now(self) -> datetime: ...
