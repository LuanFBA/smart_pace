from __future__ import annotations

from datetime import date
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from smart_pace.domain.entities.workout_log import WorkoutLog
from smart_pace.domain.repositories.workout_log_repository import (
    WorkoutLogRepository as WorkoutLogRepositoryPort,
)
from smart_pace.infrastructure.database.mappers import (
    workout_log_entity_to_model,
    workout_log_model_to_entity,
)
from smart_pace.infrastructure.database.models import WorkoutLogModel


class SqlAlchemyWorkoutLogRepository(WorkoutLogRepositoryPort):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, log_id: UUID) -> WorkoutLog | None:
        result = await self._session.get(WorkoutLogModel, log_id)
        return workout_log_model_to_entity(result) if result else None

    async def find_by_athlete_profile_id(
        self,
        athlete_profile_id: UUID,
        limit: int = 20,
        offset: int = 0,
    ) -> list[WorkoutLog]:
        stmt = (
            select(WorkoutLogModel)
            .where(WorkoutLogModel.athlete_profile_id == athlete_profile_id)
            .order_by(WorkoutLogModel.started_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        return [workout_log_model_to_entity(m) for m in result.scalars().all()]

    async def find_since_date(
        self,
        athlete_profile_id: UUID,
        since: date,
    ) -> list[WorkoutLog]:
        stmt = (
            select(WorkoutLogModel)
            .where(WorkoutLogModel.athlete_profile_id == athlete_profile_id)
            .where(WorkoutLogModel.started_at >= since)
            .order_by(WorkoutLogModel.started_at.asc())
        )
        result = await self._session.execute(stmt)
        return [workout_log_model_to_entity(m) for m in result.scalars().all()]

    async def find_by_workout_session_id(
        self, workout_session_id: UUID
    ) -> WorkoutLog | None:
        stmt = select(WorkoutLogModel).where(
            WorkoutLogModel.workout_session_id == workout_session_id
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return workout_log_model_to_entity(model) if model else None

    async def count_by_athlete_profile_id(self, athlete_profile_id: UUID) -> int:
        stmt = select(func.count()).where(
            WorkoutLogModel.athlete_profile_id == athlete_profile_id
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def save(self, log: WorkoutLog) -> WorkoutLog:
        model = workout_log_entity_to_model(log)
        merged = await self._session.merge(model)
        await self._session.flush()
        return workout_log_model_to_entity(merged)

    async def delete(self, log_id: UUID) -> None:
        model = await self._session.get(WorkoutLogModel, log_id)
        if model:
            await self._session.delete(model)
            await self._session.flush()
