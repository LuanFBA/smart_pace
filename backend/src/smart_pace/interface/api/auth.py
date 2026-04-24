"""Rotas de autenticação."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Response, status

from smart_pace.application.dtos.auth import (
    AuthTokensOutput,
    DeactivateAccountInput,
    LoginInput,
    RefreshTokenInput,
    RegisterUserInput,
)
from smart_pace.application.ports.token_service import TokenPayload
from smart_pace.infrastructure.container import Container
from smart_pace.interface.dependencies import get_container, get_current_user

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post(
    "/register",
    response_model=AuthTokensOutput,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    body: RegisterUserInput,
    container: Container = Depends(get_container),
) -> AuthTokensOutput:
    """Registrar nova conta de usuário."""
    return await container.auth_use_cases().register(body)


@router.post("/login", response_model=AuthTokensOutput)
async def login(
    body: LoginInput,
    container: Container = Depends(get_container),
) -> AuthTokensOutput:
    """Fazer login."""
    return await container.auth_use_cases().login(body)


@router.post("/token/refresh", response_model=AuthTokensOutput)
async def refresh_token(
    body: RefreshTokenInput,
    container: Container = Depends(get_container),
) -> AuthTokensOutput:
    """Renovar token de acesso."""
    return await container.auth_use_cases().refresh_token(body)


@router.delete("/account", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_account(
    current_user: TokenPayload = Depends(get_current_user),
    container: Container = Depends(get_container),
) -> Response:
    """Desativar conta do usuário autenticado."""
    input_data = DeactivateAccountInput(user_id=current_user.user_id)
    await container.auth_use_cases().deactivate_account(input_data)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
