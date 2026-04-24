"""Rotas de planos de treino."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status

from smart_pace.application.dtos.training_plan import (
    ActivateTrainingPlanInput,
    CancelTrainingPlanInput,
    CreateTrainingPlanInput,
    GetTrainingPlanInput,
    ListTrainingPlansInput,
    TrainingPlanOutput,
)
from smart_pace.application.ports.token_service import TokenPayload
from smart_pace.infrastructure.container import Container
from smart_pace.interface.dependencies import get_container, get_current_user
from smart_pace.interface.api.schemas.schemas import CreateTrainingPlanRequest

router = APIRouter(prefix="/training-plans", tags=["Planos de Treino"])


@router.get("/", response_model=list[TrainingPlanOutput])
async def list_plans(
    athlete_profile_id: UUID,
    current_user: TokenPayload = Depends(get_current_user),
    container: Container = Depends(get_container),
) -> list[TrainingPlanOutput]:
    """Listar planos de treino do atleta."""
    input_data = ListTrainingPlansInput(
        athlete_profile_id=athlete_profile_id,
        user_id=current_user.user_id,
    )
    return await container.training_use_cases().list_plans(input_data)


@router.get("/{plan_id}", response_model=TrainingPlanOutput)
async def get_plan(
    plan_id: UUID,
    current_user: TokenPayload = Depends(get_current_user),
    container: Container = Depends(get_container),
) -> TrainingPlanOutput:
    """Consultar plano de treino específico."""
    input_data = GetTrainingPlanInput(
        plan_id=plan_id,
        user_id=current_user.user_id,
    )
    return await container.training_use_cases().get_plan(input_data)


@router.post(
    "/",
    response_model=TrainingPlanOutput,
    status_code=status.HTTP_201_CREATED,
)
async def create_plan(
    body: CreateTrainingPlanRequest,
    current_user: TokenPayload = Depends(get_current_user),
    container: Container = Depends(get_container),
) -> TrainingPlanOutput:
    """Criar novo plano de treino."""
    input_data = CreateTrainingPlanInput(
        athlete_profile_id=body.athlete_profile_id,
        user_id=current_user.user_id,
        name=body.name,
        goal_description=body.goal_description,
        start_date=body.start_date,
        end_date=body.end_date,
        sport_type=body.sport_type,
    )
    return await container.training_use_cases().create_plan(input_data)


@router.post("/{plan_id}/activate", response_model=TrainingPlanOutput)
async def activate_plan(
    plan_id: UUID,
    current_user: TokenPayload = Depends(get_current_user),
    container: Container = Depends(get_container),
) -> TrainingPlanOutput:
    """Ativar plano de treino."""
    input_data = ActivateTrainingPlanInput(
        plan_id=plan_id,
        user_id=current_user.user_id,
    )
    return await container.training_use_cases().activate_plan(input_data)


@router.post("/{plan_id}/cancel", response_model=TrainingPlanOutput)
async def cancel_plan(
    plan_id: UUID,
    current_user: TokenPayload = Depends(get_current_user),
    container: Container = Depends(get_container),
) -> TrainingPlanOutput:
    """Cancelar plano de treino."""
    input_data = CancelTrainingPlanInput(
        plan_id=plan_id,
        user_id=current_user.user_id,
    )
    return await container.training_use_cases().cancel_plan(input_data)
