from __future__ import annotations

from collections.abc import Callable

from smart_pace.application.dtos.auth import (
    AuthTokensOutput,
    DeactivateAccountInput,
    LoginInput,
    RefreshTokenInput,
    RegisterUserInput,
)
from smart_pace.application.ports.password_hasher import PasswordHasher
from smart_pace.application.ports.token_service import TokenPayload, TokenService
from smart_pace.application.ports.unit_of_work import UnitOfWork
from smart_pace.domain.entities.user import User
from smart_pace.domain.exceptions import (
    ConflictException,
    EntityNotFoundException,
    InvalidDataException,
    UnauthorizedException,
)
from smart_pace.domain.value_objects.email_address import EmailAddress

_MIN_PASSWORD_LENGTH = 8


class AuthUseCases:
    def __init__(
        self,
        unit_of_work: Callable[[], UnitOfWork],
        password_hasher: PasswordHasher,
        token_service: TokenService,
    ) -> None:
        self.unit_of_work = unit_of_work
        self.password_hasher = password_hasher
        self.token_service = token_service

    async def register(self, input_data: RegisterUserInput) -> AuthTokensOutput:
        """UC1 — Registrar conta."""
        if len(input_data.password) < _MIN_PASSWORD_LENGTH:
            raise InvalidDataException(
                f"Password must be at least {_MIN_PASSWORD_LENGTH} characters"
            )

        email = EmailAddress(input_data.email)

        async with self.unit_of_work() as uow:
            existing_user = await uow.users.find_by_email(email)
            if existing_user is not None:
                raise ConflictException("Email already registered")

            hashed_password = self.password_hasher.hash_password(input_data.password)
            user = User(
                email=email,
                password_hash=hashed_password,
                full_name=input_data.full_name,
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
        payload = self.token_service.decode_token(input_data.refresh_token)

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

            user.deactivate()
            await uow.users.save(user)
            await uow.commit()
