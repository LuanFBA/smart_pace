"""Ponto de entrada da aplicação FastAPI."""

from __future__ import annotations

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from smart_pace.infrastructure.container import Container
from smart_pace.infrastructure.observability.logging import configure_logging
from smart_pace.infrastructure.observability.tracing import (
    instrument_fastapi,
    instrument_sqlalchemy,
    setup_tracing,
)
from smart_pace.infrastructure.middleware.request_logging import RequestLoggingMiddleware
from smart_pace.infrastructure.settings import Settings
from smart_pace.interface.api import auth, metrics, profiles, training_plans, workouts
from smart_pace.interface.exception_handlers import register_exception_handlers


_settings = Settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Gerencia o ciclo de vida da aplicação (startup/shutdown)."""
    # Logging estruturado — deve ser o primeiro a inicializar
    configure_logging(
        log_level=_settings.log_level,
        log_format=_settings.log_format,
        service_name=_settings.otel_service_name,
        environment=_settings.environment,
    )

    # OpenTelemetry — inicializa antes do container para instrumentar o engine
    otel_provider = None
    if _settings.otel_enabled:
        otel_provider = setup_tracing(
            service_name=_settings.otel_service_name,
            otlp_endpoint=_settings.otel_exporter_otlp_endpoint,
            environment=_settings.environment,
        )
        instrument_fastapi(app)

    # Container de DI
    container = Container(_settings)
    app.state.container = container

    # Instrumenta o engine do SQLAlchemy após o container criá-lo
    if _settings.otel_enabled:
        instrument_sqlalchemy(container.engine)

    yield

    # Shutdown: libera recursos na ordem inversa
    await container.close()
    if otel_provider is not None:
        otel_provider.shutdown()


app = FastAPI(
    title="Smart Pace API",
    version="0.1.0",
    description="Plataforma inteligente de treinos para corrida e ciclismo.",
    lifespan=lifespan,
)

# CORS configurável via SMART_PACE_CORS_ALLOWED_ORIGINS — deve ser registrado antes do startup
_origins = [o.strip() for o in _settings.cors_allowed_origins.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware de logging de requests — registrado após CORS para logar apenas requests válidos
app.add_middleware(RequestLoggingMiddleware)

register_exception_handlers(app)

# Routers agrupados sob /api/v1
api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(auth.router)
api_v1_router.include_router(profiles.router)
api_v1_router.include_router(training_plans.router)
api_v1_router.include_router(workouts.router)
api_v1_router.include_router(metrics.router)

app.include_router(api_v1_router)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Verificação de saúde da aplicação."""
    return {"status": "ok"}
