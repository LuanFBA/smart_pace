from __future__ import annotations

import bcrypt

from smart_pace.application.ports.password_hasher import PasswordHasher


class BcryptPasswordHasher(PasswordHasher):
    """Implementação de PasswordHasher usando bcrypt."""

    def hash_password(self, plain_password: str) -> str:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(plain_password.encode("utf-8"), salt)
        return hashed.decode("utf-8")

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
