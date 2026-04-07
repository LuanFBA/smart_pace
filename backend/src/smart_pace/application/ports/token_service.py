from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class TokenPayload:
    """Dados contidos no token JWT."""

    user_id: UUID
    email: str


class TokenService(ABC):
    """Abstração para criação e validação de tokens JWT."""

    @abstractmethod
    def create_access_token(self, payload: TokenPayload) -> str: ...

    @abstractmethod
    def create_refresh_token(self, payload: TokenPayload) -> str: ...

    @abstractmethod
    def decode_token(self, token: str) -> TokenPayload: ...
