from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from smart_pace.domain.entities.workout_session import WorkoutSession


class WorkoutSessionRepository(ABC):
    @abstractmethod
    async def find_by_id(self, session_id: UUID) -> WorkoutSession | None: ...

    @abstractmethod
    async def find_by_athlete_profile_id(
        self,
        athlete_profile_id: UUID,
        limit: int = 20,
        offset: int = 0,
    ) -> list[WorkoutSession]: ...

    @abstractmethod
    async def find_by_training_block_id(
        self, training_block_id: UUID
    ) -> list[WorkoutSession]: ...

    @abstractmethod
    async def save(self, session: WorkoutSession) -> WorkoutSession: ...
