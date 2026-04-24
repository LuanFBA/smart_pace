from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from smart_pace.domain.entities.performance_metrics import PerformanceMetrics


class PerformanceMetricsRepository(ABC):
    @abstractmethod
    async def find_by_id(self, metrics_id: UUID) -> PerformanceMetrics | None: ...

    @abstractmethod
    async def find_latest_by_athlete_profile_id(
        self, athlete_profile_id: UUID
    ) -> PerformanceMetrics | None: ...

    @abstractmethod
    async def save(self, metrics: PerformanceMetrics) -> PerformanceMetrics: ...
