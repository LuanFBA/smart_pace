"""Handlers globais de exceção — mapeia erros de domínio para respostas HTTP."""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from smart_pace.domain.exceptions import (
    ConflictException,
    DomainException,
    EntityNotFoundException,
    InvalidDataException,
    UnauthorizedException,
)


def register_exception_handlers(app: FastAPI) -> None:
    """Registra handlers que convertem exceções de domínio em respostas HTTP."""

    @app.exception_handler(EntityNotFoundException)
    async def _entity_not_found(
        request: Request, exc: EntityNotFoundException
    ) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": exc.message})

    @app.exception_handler(UnauthorizedException)
    async def _unauthorized(
        request: Request, exc: UnauthorizedException
    ) -> JSONResponse:
        return JSONResponse(status_code=401, content={"detail": exc.message})

    @app.exception_handler(ConflictException)
    async def _conflict(request: Request, exc: ConflictException) -> JSONResponse:
        return JSONResponse(status_code=409, content={"detail": exc.message})

    @app.exception_handler(InvalidDataException)
    async def _invalid_data(
        request: Request, exc: InvalidDataException
    ) -> JSONResponse:
        return JSONResponse(status_code=422, content={"detail": exc.message})

    @app.exception_handler(DomainException)
    async def _domain_error(request: Request, exc: DomainException) -> JSONResponse:
        return JSONResponse(status_code=400, content={"detail": exc.message})

    @app.exception_handler(Exception)
    async def _unhandled_error(request: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=500, content={"detail": "Internal server error"}
        )
