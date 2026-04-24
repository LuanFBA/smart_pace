from __future__ import annotations

from typing import Literal

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configurações carregadas de variáveis de ambiente."""

    # Banco de dados
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/smart_pace"

    # CORS
    cors_allowed_origins: str = "*"

    # JWT
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7

    # Logging
    log_level: str = "INFO"
    log_format: Literal["json", "console"] = "json"
    environment: str = "production"

    # OpenTelemetry
    otel_enabled: bool = True
    otel_exporter_otlp_endpoint: str = "http://localhost:4318"
    otel_service_name: str = "smart_pace"

    model_config = {"env_prefix": "SMART_PACE_"}
