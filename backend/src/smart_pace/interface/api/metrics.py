"""Rotas de métricas de performance."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends

from smart_pace.application.dtos.metrics import (
    PerformanceDashboardOutput,
    ViewPerformanceDashboardInput,
)
from smart_pace.application.ports.token_service import TokenPayload
from smart_pace.infrastructure.container import Container
from smart_pace.interface.dependencies import get_container, get_current_user

router = APIRouter(prefix="/metrics", tags=["Métricas de Performance"])


@router.get("/dashboard", response_model=PerformanceDashboardOutput)
async def get_dashboard(
    athlete_profile_id: UUID,
    current_user: TokenPayload = Depends(get_current_user),
    container: Container = Depends(get_container),
) -> PerformanceDashboardOutput:
    """Ver dashboard de evolução do atleta."""
    input_data = ViewPerformanceDashboardInput(
        athlete_profile_id=athlete_profile_id,
        user_id=current_user.user_id,
    )
    return await container.metrics_use_cases().view_dashboard(input_data)
