from __future__ import annotations

from collections.abc import Callable

from smart_pace.application.dtos.auth import (
    AuthTokensOutput,
    DeactivateAccountInput,
    LoginInput,
    RefreshTokenInput,
    RegisterUserInput,
)
from smart_pace.application.ports.clock import Clock
from smart_pace.application.ports.password_hasher import PasswordHasher
from smart_pace.application.ports.token_service import TokenPayload, TokenService
from smart_pace.application.ports.unit_of_work import UnitOfWork
from smart_pace.domain.entities.user import User
from smart_pace.domain.exceptions import (
    ConflictException,
    EntityNotFoundException,
    UnauthorizedException,
)
from smart_pace.domain.value_objects.email_address import EmailAddress
from smart_pace.domain.value_objects.password import Password


# Hash pre-computado para manter tempo constante quando usuario nao existe
_DUMMY_HASH = "$2b$12$WpfsqOVKAk/oij9tLi08T.FE2psbdQAvRYNJM7MElId5qgZmJ.sBy"


class AuthUseCases:
    def __init__(
        self,
        unit_of_work: Callable[[], UnitOfWork],
        password_hasher: PasswordHasher,
        token_service: TokenService,
        clock: Clock,
    ) -> None:
        self.unit_of_work = unit_of_work
        self.password_hasher = password_hasher
        self.token_service = token_service
        self.clock = clock

    async def register(self, input_data: RegisterUserInput) -> AuthTokensOutput:
        """UC1 — Registrar conta."""
        Password(input_data.password)  # valida regras de domínio
        email = EmailAddress(input_data.email)

        now = self.clock.now()

        async with self.unit_of_work() as uow:
            existing_user = await uow.users.find_by_email(email)
            if existing_user is not None:
                raise ConflictException("Email already registered")

            hashed_password = self.password_hasher.hash_password(input_data.password)
            user = User(
                email=email,
                password_hash=hashed_password,
                full_name=input_data.full_name,
                created_at=now,
                updated_at=now,
            )
            await uow.users.save(user)
            await uow.commit()

        payload = TokenPayload(user_id=user.id, email=user.email.value)
        return AuthTokensOutput(
            access_token=self.token_service.create_access_token(payload),
            refresh_token=self.token_service.create_refresh_token(payload),
        )

    async def login(self, input_data: LoginInput) -> AuthTokensOutput:
        """UC2 — Fazer login."""
        email = EmailAddress(input_data.email)

        async with self.unit_of_work() as uow:
            user = await uow.users.find_by_email(email)

        if user is None:
            # Consome tempo equivalente ao bcrypt para evitar timing attack
            self.password_hasher.verify_password(input_data.password, _DUMMY_HASH)
            raise UnauthorizedException("Invalid credentials")

        if not user.is_active:
            raise UnauthorizedException("Account is deactivated")

        if not self.password_hasher.verify_password(
            input_data.password, user.password_hash
        ):
            raise UnauthorizedException("Invalid credentials")

        payload = TokenPayload(user_id=user.id, email=user.email.value)
        return AuthTokensOutput(
            access_token=self.token_service.create_access_token(payload),
            refresh_token=self.token_service.create_refresh_token(payload),
        )

    async def refresh_token(self, input_data: RefreshTokenInput) -> AuthTokensOutput:
        """UC3 — Renovar token."""
        payload = self.token_service.decode_token(
            input_data.refresh_token, expected_type="refresh"
        )

        async with self.unit_of_work() as uow:
            user = await uow.users.find_by_id(payload.user_id)

        if user is None or not user.is_active:
            raise UnauthorizedException("Invalid or expired token")

        new_payload = TokenPayload(user_id=user.id, email=user.email.value)
        return AuthTokensOutput(
            access_token=self.token_service.create_access_token(new_payload),
            refresh_token=self.token_service.create_refresh_token(new_payload),
        )

    async def deactivate_account(self, input_data: DeactivateAccountInput) -> None:
        """UC4 — Desativar conta."""
        async with self.unit_of_work() as uow:
            user = await uow.users.find_by_id(input_data.user_id)
            if user is None:
                raise EntityNotFoundException("User not found")

            user.deactivate(now=self.clock.now())
            await uow.users.save(user)
            await uow.commit()
