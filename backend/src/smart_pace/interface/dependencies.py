"""Dependências injetáveis via FastAPI Depends()."""

from __future__ import annotations

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from smart_pace.application.ports.token_service import TokenPayload
from smart_pace.infrastructure.container import Container

# HTTPBearer registra o esquema Bearer no OpenAPI → botão "Authorize" no Swagger
_bearer = HTTPBearer()


def get_container(request: Request) -> Container:
    """Obtém o container de DI armazenado no estado da aplicação."""
    return request.app.state.container


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
    container: Container = Depends(get_container),
) -> TokenPayload:
    """Extrai e valida o token JWT do header Authorization."""
    # decode_token levanta UnauthorizedException se token inválido,
    # que é capturada pelo exception_handler global (→ 401)
    return container.token_service.decode_token(credentials.credentials)
