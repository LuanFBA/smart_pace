from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4

from smart_pace.domain.exceptions import InvalidDataException
from smart_pace.domain.value_objects.email_address import EmailAddress


@dataclass
class User:
    email: EmailAddress
    password_hash: str
    full_name: str
    id: UUID = field(default_factory=uuid4)
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        if not self.full_name.strip():
            raise InvalidDataException("full_name cannot be empty")

    def deactivate(self, now: datetime) -> None:
        self.is_active = False
        self.updated_at = now

    def change_email(self, new_email: EmailAddress, now: datetime) -> None:
        self.email = new_email
        self.updated_at = now
