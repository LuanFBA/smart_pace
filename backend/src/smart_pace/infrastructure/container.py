"""Container de injeção de dependências.

Responsável por criar e conectar todas as peças da infraestrutura
com a camada de application. Sem framework de DI — composição manual.
"""

from __future__ import annotations

from smart_pace.application.ports.clock import Clock
from smart_pace.application.ports.password_hasher import PasswordHasher
from smart_pace.application.ports.token_service import TokenService
from smart_pace.application.ports.unit_of_work import UnitOfWork
from smart_pace.application.use_cases.auth_use_cases import AuthUseCases
from smart_pace.application.use_cases.metrics_use_cases import MetricsUseCases
from smart_pace.application.use_cases.profile_use_cases import ProfileUseCases
from smart_pace.application.use_cases.training_use_cases import TrainingUseCases
from smart_pace.application.use_cases.workout_use_cases import WorkoutUseCases
from smart_pace.infrastructure.database.session import (
    create_engine,
    create_session_factory,
)
from smart_pace.infrastructure.services.bcrypt_password_hasher import (
    BcryptPasswordHasher,
)
from smart_pace.infrastructure.services.jwt_token_service import JwtTokenService
from smart_pace.infrastructure.services.system_clock import SystemClock
from smart_pace.infrastructure.settings import Settings
from smart_pace.infrastructure.unit_of_work import SqlAlchemyUnitOfWork


class Container:
    """Composição raiz — cria e expõe todos os use cases prontos para uso."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or Settings()
        self._engine = create_engine(self._settings.database_url)
        self._session_factory = create_session_factory(self._engine)

        # Ports
        self._clock: Clock = SystemClock()
        self._password_hasher: PasswordHasher = BcryptPasswordHasher()
        self._token_service: TokenService = JwtTokenService(
            secret_key=self._settings.jwt_secret_key,
            algorithm=self._settings.jwt_algorithm,
            access_token_expire_minutes=self._settings.jwt_access_token_expire_minutes,
            refresh_token_expire_days=self._settings.jwt_refresh_token_expire_days,
        )

    @property
    def engine(self) -> object:
        """Expõe o engine para instrumentação externa (ex: OpenTelemetry)."""
        return self._engine

    @property
    def token_service(self) -> TokenService:
        """Expõe o serviço de tokens para uso na camada de interface."""
        return self._token_service

    def _uow_factory(self) -> UnitOfWork:
        """Fábrica de UnitOfWork — cria nova instância por request."""
        return SqlAlchemyUnitOfWork(self._session_factory)

    # ── Use Cases ────────────────────────────

    def auth_use_cases(self) -> AuthUseCases:
        return AuthUseCases(
            unit_of_work=self._uow_factory,
            password_hasher=self._password_hasher,
            token_service=self._token_service,
            clock=self._clock,
        )

    def profile_use_cases(self) -> ProfileUseCases:
        return ProfileUseCases(unit_of_work=self._uow_factory)

    def training_use_cases(self) -> TrainingUseCases:
        return TrainingUseCases(unit_of_work=self._uow_factory)

    def workout_use_cases(self) -> WorkoutUseCases:
        return WorkoutUseCases(
            unit_of_work=self._uow_factory,
            clock=self._clock,
        )

    def metrics_use_cases(self) -> MetricsUseCases:
        return MetricsUseCases(unit_of_work=self._uow_factory)

    async def close(self) -> None:
        """Libera recursos (engine/pool de conexões)."""
        await self._engine.dispose()
