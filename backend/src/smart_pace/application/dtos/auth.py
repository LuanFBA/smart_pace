from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class RegisterUserInput(BaseModel):
    model_config = ConfigDict(frozen=True)

    email: str
    password: str
    full_name: str


class LoginInput(BaseModel):
    model_config = ConfigDict(frozen=True)

    email: str
    password: str


class RefreshTokenInput(BaseModel):
    model_config = ConfigDict(frozen=True)

    refresh_token: str


class DeactivateAccountInput(BaseModel):
    model_config = ConfigDict(frozen=True)

    user_id: UUID


class AuthTokensOutput(BaseModel):
    model_config = ConfigDict(frozen=True)

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserOutput(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: UUID
    email: str
    full_name: str
    is_active: bool
    created_at: datetime
