"""Setup do OpenTelemetry TracerProvider com exporter OTLP HTTP."""

from __future__ import annotations

import structlog
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

logger = structlog.get_logger(__name__)


def setup_tracing(
    service_name: str,
    otlp_endpoint: str,
    environment: str,
) -> TracerProvider:
    """Inicializa o TracerProvider com exporter OTLP e auto-instrumentação.

    Deve ser chamado no startup da aplicação, antes do yield do lifespan.
    Retorna o provider para que o caller possa fazer shutdown no teardown.
    """
    resource = Resource.create(
        {
            "service.name": service_name,
            "deployment.environment": environment,
        }
    )

    exporter = OTLPSpanExporter(endpoint=f"{otlp_endpoint}/v1/traces")
    provider = TracerProvider(resource=resource)
    provider.add_span_processor(BatchSpanProcessor(exporter))

    # Registra como provider global — usado pelas auto-instrumentações
    trace.set_tracer_provider(provider)

    logger.info(
        "OpenTelemetry tracing initialized",
        service=service_name,
        otlp_endpoint=otlp_endpoint,
    )

    return provider


def instrument_fastapi(app: object) -> None:
    """Ativa auto-instrumentação do FastAPI."""
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

    FastAPIInstrumentor.instrument_app(app)  # type: ignore[arg-type]


def instrument_sqlalchemy(engine: object) -> None:
    """Ativa auto-instrumentação do SQLAlchemy.

    Para AsyncEngine, a instrumentação precisa ser aplicada ao sync_engine
    subjacente — eventos assíncronos não são suportados pelo SQLAlchemy.
    """
    from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
    from sqlalchemy.ext.asyncio import AsyncEngine

    target = engine.sync_engine if isinstance(engine, AsyncEngine) else engine
    SQLAlchemyInstrumentor().instrument(engine=target)  # type: ignore[arg-type]
