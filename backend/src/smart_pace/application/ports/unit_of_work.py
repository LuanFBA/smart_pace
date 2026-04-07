from __future__ import annotations

from abc import ABC, abstractmethod
from types import TracebackType

from smart_pace.domain.repositories import (
    AthleteProfileRepository,
    PerformanceMetricsRepository,
    TrainingBlockRepository,
    TrainingPlanRepository,
    UserRepository,
    WorkoutLogRepository,
    WorkoutSessionRepository,
)


class UnitOfWork(ABC):
    """Fronteira transacional que expõe todos os repositórios.

    Uso típico:
        async with unit_of_work() as uow:
            user = await uow.users.find_by_id(user_id)
            ...
            await uow.commit()

    Se uma exceção propagar, __aexit__ faz rollback automaticamente.
    """

    users: UserRepository
    athlete_profiles: AthleteProfileRepository
    training_plans: TrainingPlanRepository
    training_blocks: TrainingBlockRepository
    workout_sessions: WorkoutSessionRepository
    workout_logs: WorkoutLogRepository
    performance_metrics: PerformanceMetricsRepository

    @abstractmethod
    async def commit(self) -> None: ...

    @abstractmethod
    async def rollback(self) -> None: ...

    @abstractmethod
    async def __aenter__(self) -> UnitOfWork: ...

    @abstractmethod
    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None: ...
