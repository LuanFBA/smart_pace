from __future__ import annotations

from types import TracebackType

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from smart_pace.application.ports.unit_of_work import UnitOfWork
from smart_pace.infrastructure.repositories.athlete_profile_repository import (
    SqlAlchemyAthleteProfileRepository,
)
from smart_pace.infrastructure.repositories.performance_metrics_repository import (
    SqlAlchemyPerformanceMetricsRepository,
)
from smart_pace.infrastructure.repositories.training_block_repository import (
    SqlAlchemyTrainingBlockRepository,
)
from smart_pace.infrastructure.repositories.training_plan_repository import (
    SqlAlchemyTrainingPlanRepository,
)
from smart_pace.infrastructure.repositories.user_repository import (
    SqlAlchemyUserRepository,
)
from smart_pace.infrastructure.repositories.workout_log_repository import (
    SqlAlchemyWorkoutLogRepository,
)
from smart_pace.infrastructure.repositories.workout_session_repository import (
    SqlAlchemyWorkoutSessionRepository,
)


class SqlAlchemyUnitOfWork(UnitOfWork):
    """Implementação concreta do UnitOfWork usando SQLAlchemy async.

    Cada instância cria uma sessão nova. A sessão é fechada
    ao sair do context manager, com rollback automático em exceções.
    """

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def __aenter__(self) -> SqlAlchemyUnitOfWork:
        self._session = self._session_factory()

        # Instancia repositórios com a sessão compartilhada
        self.users = SqlAlchemyUserRepository(self._session)
        self.athlete_profiles = SqlAlchemyAthleteProfileRepository(self._session)
        self.training_plans = SqlAlchemyTrainingPlanRepository(self._session)
        self.training_blocks = SqlAlchemyTrainingBlockRepository(self._session)
        self.workout_sessions = SqlAlchemyWorkoutSessionRepository(self._session)
        self.workout_logs = SqlAlchemyWorkoutLogRepository(self._session)
        self.performance_metrics = SqlAlchemyPerformanceMetricsRepository(self._session)

        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if exc_type is not None:
            await self.rollback()
        await self._session.close()

    async def commit(self) -> None:
        await self._session.commit()

    async def rollback(self) -> None:
        await self._session.rollback()
