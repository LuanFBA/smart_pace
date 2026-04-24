from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from smart_pace.domain.entities.performance_metrics import PerformanceMetrics
from smart_pace.domain.repositories.performance_metrics_repository import (
    PerformanceMetricsRepository as PerformanceMetricsRepositoryPort,
)
from smart_pace.infrastructure.database.mappers import (
    performance_metrics_entity_to_model,
    performance_metrics_model_to_entity,
)
from smart_pace.infrastructure.database.models import PerformanceMetricsModel


class SqlAlchemyPerformanceMetricsRepository(PerformanceMetricsRepositoryPort):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, metrics_id: UUID) -> PerformanceMetrics | None:
        result = await self._session.get(PerformanceMetricsModel, metrics_id)
        return performance_metrics_model_to_entity(result) if result else None

    async def find_latest_by_athlete_profile_id(
        self, athlete_profile_id: UUID
    ) -> PerformanceMetrics | None:
        stmt = (
            select(PerformanceMetricsModel)
            .where(
                PerformanceMetricsModel.athlete_profile_id == athlete_profile_id
            )
            .order_by(PerformanceMetricsModel.calculated_at.desc())
            .limit(1)
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return performance_metrics_model_to_entity(model) if model else None

    async def save(self, metrics: PerformanceMetrics) -> PerformanceMetrics:
        model = performance_metrics_entity_to_model(metrics)
        merged = await self._session.merge(model)
        await self._session.flush()
        return performance_metrics_model_to_entity(merged)
