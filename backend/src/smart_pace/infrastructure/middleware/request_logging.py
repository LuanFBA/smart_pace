"""Middleware ASGI para logging de requests e responses HTTP."""

from __future__ import annotations

import time
from collections.abc import Callable

import structlog
from starlette.types import ASGIApp, Receive, Scope, Send

logger = structlog.get_logger(__name__)


class RequestLoggingMiddleware:
    """Middleware ASGI que loga metadados de cada request/response.

    Loga apenas metadados (method, path, status_code, duration_ms).
    O body nunca é lido ou logado.

    O trace_id é injetado automaticamente via _add_otel_trace_context
    configurado no structlog — não é necessário extrair aqui manualmente.
    """

    def __init__(self, app: ASGIApp) -> None:
        self._app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            # Ignora conexões WebSocket e lifespan
            await self._app(scope, receive, send)
            return

        method: str = scope.get("method", "")
        path: str = scope.get("path", "")
        start_time = time.perf_counter()

        # Captura o status code interceptando o início da resposta
        status_code: int = 0

        async def send_wrapper(message: object) -> None:
            nonlocal status_code
            if isinstance(message, dict) and message.get("type") == "http.response.start":
                status_code = message.get("status", 0)  # type: ignore[assignment]
            await send(message)  # type: ignore[arg-type]

        try:
            await self._app(scope, receive, send_wrapper)
        finally:
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            logger.info(
                "request_finished",
                method=method,
                path=path,
                status_code=status_code,
                duration_ms=duration_ms,
            )
