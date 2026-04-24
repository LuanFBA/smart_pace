from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from smart_pace.domain.entities.training_block import TrainingBlock
from smart_pace.domain.repositories.training_block_repository import (
    TrainingBlockRepository as TrainingBlockRepositoryPort,
)
from smart_pace.infrastructure.database.mappers import (
    training_block_entity_to_model,
    training_block_model_to_entity,
)
from smart_pace.infrastructure.database.models import TrainingBlockModel


class SqlAlchemyTrainingBlockRepository(TrainingBlockRepositoryPort):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, block_id: UUID) -> TrainingBlock | None:
        result = await self._session.get(TrainingBlockModel, block_id)
        return training_block_model_to_entity(result) if result else None

    async def find_by_training_plan_id(
        self, training_plan_id: UUID
    ) -> list[TrainingBlock]:
        stmt = (
            select(TrainingBlockModel)
            .where(TrainingBlockModel.training_plan_id == training_plan_id)
            .order_by(TrainingBlockModel.week_number)
        )
        result = await self._session.execute(stmt)
        return [training_block_model_to_entity(m) for m in result.scalars().all()]

    async def save(self, block: TrainingBlock) -> TrainingBlock:
        model = training_block_entity_to_model(block)
        merged = await self._session.merge(model)
        await self._session.flush()
        return training_block_model_to_entity(merged)

    async def delete(self, block_id: UUID) -> None:
        model = await self._session.get(TrainingBlockModel, block_id)
        if model:
            await self._session.delete(model)
            await self._session.flush()
