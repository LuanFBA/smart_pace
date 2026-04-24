from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from smart_pace.domain.entities.user import User
from smart_pace.domain.repositories.user_repository import (
    UserRepository as UserRepositoryPort,
)
from smart_pace.domain.value_objects.email_address import EmailAddress
from smart_pace.infrastructure.database.mappers import (
    user_entity_to_model,
    user_model_to_entity,
)
from smart_pace.infrastructure.database.models import UserModel


class SqlAlchemyUserRepository(UserRepositoryPort):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, user_id: UUID) -> User | None:
        result = await self._session.get(UserModel, user_id)
        return user_model_to_entity(result) if result else None

    async def find_by_email(self, email: EmailAddress) -> User | None:
        stmt = select(UserModel).where(UserModel.email == email.value)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return user_model_to_entity(model) if model else None

    async def save(self, user: User) -> User:
        model = user_entity_to_model(user)
        merged = await self._session.merge(model)
        await self._session.flush()
        return user_model_to_entity(merged)

    async def delete(self, user_id: UUID) -> None:
        model = await self._session.get(UserModel, user_id)
        if model:
            await self._session.delete(model)
            await self._session.flush()
