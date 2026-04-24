from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from smart_pace.domain.entities.training_plan import TrainingPlan


class TrainingPlanRepository(ABC):
    @abstractmethod
    async def find_by_id(self, plan_id: UUID) -> TrainingPlan | None: ...

    @abstractmethod
    async def find_by_athlete_profile_id(
        self, athlete_profile_id: UUID
    ) -> list[TrainingPlan]: ...

    @abstractmethod
    async def save(self, plan: TrainingPlan) -> TrainingPlan: ...

    @abstractmethod
    async def delete(self, plan_id: UUID) -> None: ...
