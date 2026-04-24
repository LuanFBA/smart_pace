"""Configuração de logging estruturado com structlog."""

from __future__ import annotations

import logging
import sys
from typing import Any

import structlog
from structlog.types import EventDict, Processor


def _add_otel_trace_context(
    logger: Any,
    method_name: str,
    event_dict: EventDict,
) -> EventDict:
    """Injeta trace_id e span_id do span OpenTelemetry ativo, se houver."""
    try:
        from opentelemetry import trace

        span = trace.get_current_span()
        span_context = span.get_span_context()

        if span_context.is_valid:
            event_dict["trace_id"] = format(span_context.trace_id, "032x")
            event_dict["span_id"] = format(span_context.span_id, "016x")
    except ImportError:
        # OpenTelemetry não disponível — ignora silenciosamente
        pass

    return event_dict


def configure_logging(
    log_level: str,
    log_format: str,
    service_name: str,
    environment: str,
) -> None:
    """Configura structlog para logging estruturado.

    Deve ser chamado uma única vez no startup da aplicação.
    Em produção usa renderer JSON; em desenvolvimento usa renderer colorido.
    """
    level = getattr(logging, log_level.upper(), logging.INFO)

    # Processadores compartilhados entre todos os renderers
    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        _add_otel_trace_context,
        # Adiciona campos fixos de serviço
        structlog.processors.CallsiteParameterAdder([]),
    ]

    def add_service_fields(
        logger: Any, method_name: str, event_dict: EventDict
    ) -> EventDict:
        """Injeta service e environment em todos os logs."""
        event_dict.setdefault("service", service_name)
        event_dict.setdefault("environment", environment)
        return event_dict

    shared_processors.insert(0, add_service_fields)

    if log_format == "json":
        renderer: Processor = structlog.processors.JSONRenderer()
    else:
        # Modo desenvolvimento — logs coloridos legíveis no terminal
        renderer = structlog.dev.ConsoleRenderer(colors=True)

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        wrapper_class=structlog.make_filtering_bound_logger(level),
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configura o handler da stdlib para usar o mesmo formatter do structlog
    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=shared_processors,
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(level)

    # Silencia loggers ruidosos de bibliotecas externas
    logging.getLogger("uvicorn.access").propagate = False
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
