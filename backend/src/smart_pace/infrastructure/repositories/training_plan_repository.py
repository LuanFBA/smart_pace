from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from smart_pace.domain.entities.training_plan import TrainingPlan
from smart_pace.domain.repositories.training_plan_repository import (
    TrainingPlanRepository as TrainingPlanRepositoryPort,
)
from smart_pace.infrastructure.database.mappers import (
    training_plan_entity_to_model,
    training_plan_model_to_entity,
)
from smart_pace.infrastructure.database.models import TrainingPlanModel


class SqlAlchemyTrainingPlanRepository(TrainingPlanRepositoryPort):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, plan_id: UUID) -> TrainingPlan | None:
        result = await self._session.get(TrainingPlanModel, plan_id)
        return training_plan_model_to_entity(result) if result else None

    async def find_by_athlete_profile_id(
        self, athlete_profile_id: UUID
    ) -> list[TrainingPlan]:
        stmt = select(TrainingPlanModel).where(
            TrainingPlanModel.athlete_profile_id == athlete_profile_id
        )
        result = await self._session.execute(stmt)
        return [training_plan_model_to_entity(m) for m in result.scalars().all()]

    async def save(self, plan: TrainingPlan) -> TrainingPlan:
        model = training_plan_entity_to_model(plan)
        merged = await self._session.merge(model)
        await self._session.flush()
        return training_plan_model_to_entity(merged)

    async def delete(self, plan_id: UUID) -> None:
        model = await self._session.get(TrainingPlanModel, plan_id)
        if model:
            await self._session.delete(model)
            await self._session.flush()
