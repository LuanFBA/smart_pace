from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from uuid import UUID

from smart_pace.domain.entities.workout_log import WorkoutLog


class WorkoutLogRepository(ABC):
    @abstractmethod
    async def find_by_id(self, log_id: UUID) -> WorkoutLog | None: ...

    @abstractmethod
    async def find_since_date(
        self,
        athlete_profile_id: UUID,
        since: date,
    ) -> list[WorkoutLog]: ...

    @abstractmethod
    async def find_by_athlete_profile_id(
        self,
        athlete_profile_id: UUID,
        limit: int = 20,
        offset: int = 0,
    ) -> list[WorkoutLog]: ...

    @abstractmethod
    async def find_by_workout_session_id(
        self, workout_session_id: UUID
    ) -> WorkoutLog | None: ...

    @abstractmethod
    async def count_by_athlete_profile_id(self, athlete_profile_id: UUID) -> int: ...

    @abstractmethod
    async def save(self, log: WorkoutLog) -> WorkoutLog: ...

    @abstractmethod
    async def delete(self, log_id: UUID) -> None: ...
