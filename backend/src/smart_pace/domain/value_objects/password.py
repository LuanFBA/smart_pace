from __future__ import annotations

from dataclasses import dataclass

from smart_pace.domain.exceptions import InvalidDataException

# Tamanho mínimo de senha exigido pela política do domínio
_MIN_LENGTH = 8


@dataclass(frozen=True)
class Password:
    """Senha em texto plano, validada contra as regras de domínio."""

    value: str

    def __post_init__(self) -> None:
        if len(self.value) < _MIN_LENGTH:
            raise InvalidDataException(
                f"Password must be at least {_MIN_LENGTH} characters"
            )
