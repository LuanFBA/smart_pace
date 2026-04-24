from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from smart_pace.domain.entities.training_block import TrainingBlock


class TrainingBlockRepository(ABC):
    @abstractmethod
    async def find_by_id(self, block_id: UUID) -> TrainingBlock | None: ...

    @abstractmethod
    async def find_by_training_plan_id(
        self, training_plan_id: UUID
    ) -> list[TrainingBlock]: ...

    @abstractmethod
    async def save(self, block: TrainingBlock) -> TrainingBlock: ...

    @abstractmethod
    async def delete(self, block_id: UUID) -> None: ...
