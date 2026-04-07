from __future__ import annotations


class DomainException(Exception):
    """Exceção base para erros de domínio."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class EntityNotFoundException(DomainException):
    """Entidade não encontrada no repositório."""


class InvalidDataException(DomainException):
    """Dados inválidos para criação ou atualização de entidade."""


class UnauthorizedException(DomainException):
    """Ação não autorizada para o usuário."""


class ConflictException(DomainException):
    """Conflito com estado existente (ex: email duplicado)."""
