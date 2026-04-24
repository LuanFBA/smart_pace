from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from smart_pace.domain.entities.workout_session import WorkoutSession
from smart_pace.domain.repositories.workout_session_repository import (
    WorkoutSessionRepository as WorkoutSessionRepositoryPort,
)
from smart_pace.infrastructure.database.mappers import (
    workout_session_entity_to_model,
    workout_session_model_to_entity,
)
from smart_pace.infrastructure.database.models import WorkoutSessionModel


class SqlAlchemyWorkoutSessionRepository(WorkoutSessionRepositoryPort):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, session_id: UUID) -> WorkoutSession | None:
        result = await self._session.get(WorkoutSessionModel, session_id)
        return workout_session_model_to_entity(result) if result else None

    async def find_by_athlete_profile_id(
        self,
        athlete_profile_id: UUID,
        limit: int = 20,
        offset: int = 0,
    ) -> list[WorkoutSession]:
        stmt = (
            select(WorkoutSessionModel)
            .where(WorkoutSessionModel.athlete_profile_id == athlete_profile_id)
            .order_by(WorkoutSessionModel.scheduled_date.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        return [workout_session_model_to_entity(m) for m in result.scalars().all()]

    async def find_by_training_block_id(
        self, training_block_id: UUID
    ) -> list[WorkoutSession]:
        stmt = (
            select(WorkoutSessionModel)
            .where(WorkoutSessionModel.training_block_id == training_block_id)
            .order_by(WorkoutSessionModel.scheduled_date)
        )
        result = await self._session.execute(stmt)
        return [workout_session_model_to_entity(m) for m in result.scalars().all()]

    async def save(self, session: WorkoutSession) -> WorkoutSession:
        model = workout_session_entity_to_model(session)
        merged = await self._session.merge(model)
        await self._session.flush()
        return workout_session_model_to_entity(merged)
