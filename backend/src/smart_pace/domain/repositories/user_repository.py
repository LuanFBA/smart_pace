from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from smart_pace.domain.entities.user import User
from smart_pace.domain.value_objects.email_address import EmailAddress


class UserRepository(ABC):
    @abstractmethod
    async def find_by_id(self, user_id: UUID) -> User | None: ...

    @abstractmethod
    async def find_by_email(self, email: EmailAddress) -> User | None: ...

    @abstractmethod
    async def save(self, user: User) -> User: ...

    @abstractmethod
    async def delete(self, user_id: UUID) -> None: ...
