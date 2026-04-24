from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import UUID

from jose import JWTError, jwt

from smart_pace.application.ports.token_service import TokenPayload, TokenService
from smart_pace.domain.exceptions import UnauthorizedException


class JwtTokenService(TokenService):
    """Implementação de TokenService usando python-jose (JWT)."""

    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 30,
        refresh_token_expire_days: int = 7,
    ) -> None:
        self._secret_key = secret_key
        self._algorithm = algorithm
        self._access_expire = timedelta(minutes=access_token_expire_minutes)
        self._refresh_expire = timedelta(days=refresh_token_expire_days)

    def create_access_token(self, payload: TokenPayload) -> str:
        return self._encode(payload, self._access_expire, token_type="access")

    def create_refresh_token(self, payload: TokenPayload) -> str:
        return self._encode(payload, self._refresh_expire, token_type="refresh")

    def decode_token(
        self, token: str, expected_type: str = "access"
    ) -> TokenPayload:
        try:
            data = jwt.decode(token, self._secret_key, algorithms=[self._algorithm])
        except JWTError as err:
            raise UnauthorizedException("Invalid or expired token") from err

        try:
            token_type = data["type"]
            if token_type != expected_type:
                raise UnauthorizedException("Invalid token type")

            return TokenPayload(
                user_id=UUID(data["sub"]),
                email=data["email"],
            )
        except (KeyError, ValueError) as err:
            raise UnauthorizedException("Malformed token payload") from err

    def _encode(
        self, payload: TokenPayload, expires_delta: timedelta, token_type: str
    ) -> str:
        now = datetime.now(UTC)
        data = {
            "sub": str(payload.user_id),
            "email": payload.email,
            "type": token_type,
            "iat": now,
            "exp": now + expires_delta,
        }
        return jwt.encode(data, self._secret_key, algorithm=self._algorithm)
