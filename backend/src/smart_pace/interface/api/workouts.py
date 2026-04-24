"""Rotas de treinos (registro, histórico, sugestão)."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from smart_pace.application.dtos.workout import (
    GetNextWorkoutSuggestionInput,
    LogWorkoutInput,
    ScheduleWorkoutSessionInput,
    ViewWorkoutHistoryInput,
    WorkoutHistoryOutput,
    WorkoutLogOutput,
    WorkoutSessionOutput,
    WorkoutSuggestionOutput,
)
from smart_pace.application.ports.token_service import TokenPayload
from smart_pace.infrastructure.container import Container
from smart_pace.interface.dependencies import get_container, get_current_user
from smart_pace.interface.api.schemas.schemas import LogWorkoutRequest, ScheduleWorkoutSessionRequest

router = APIRouter(prefix="/workouts", tags=["Treinos"])


@router.post(
    "/sessions",
    response_model=WorkoutSessionOutput,
    status_code=status.HTTP_201_CREATED,
)
async def schedule_session(
    body: ScheduleWorkoutSessionRequest,
    current_user: TokenPayload = Depends(get_current_user),
    container: Container = Depends(get_container),
) -> WorkoutSessionOutput:
    """Agendar sessão de treino manualmente."""
    input_data = ScheduleWorkoutSessionInput(
        athlete_profile_id=body.athlete_profile_id,
        user_id=current_user.user_id,
        scheduled_date=body.scheduled_date,
        session_type=body.session_type,
        target_distance_meters=body.target_distance_meters,
        target_duration_seconds=body.target_duration_seconds,
        target_min_pace_seconds_per_km=body.target_min_pace_seconds_per_km,
        target_max_pace_seconds_per_km=body.target_max_pace_seconds_per_km,
    )
    return await container.workout_use_cases().schedule_session(input_data)


@router.post(
    "/log",
    response_model=WorkoutLogOutput,
    status_code=status.HTTP_201_CREATED,
)
async def log_workout(
    body: LogWorkoutRequest,
    current_user: TokenPayload = Depends(get_current_user),
    container: Container = Depends(get_container),
) -> WorkoutLogOutput:
    """Registrar sessão de treino."""
    input_data = LogWorkoutInput(
        workout_session_id=body.workout_session_id,
        athlete_profile_id=body.athlete_profile_id,
        user_id=current_user.user_id,
        started_at=body.started_at,
        finished_at=body.finished_at,
        actual_distance_meters=body.actual_distance_meters,
        actual_duration_seconds=body.actual_duration_seconds,
        average_heart_rate=body.average_heart_rate,
        maximum_heart_rate=body.maximum_heart_rate,
        perceived_exertion=body.perceived_exertion,
        notes=body.notes,
    )
    return await container.workout_use_cases().log_session(input_data)


@router.get("/history", response_model=WorkoutHistoryOutput)
async def get_workout_history(
    athlete_profile_id: UUID,
    current_user: TokenPayload = Depends(get_current_user),
    container: Container = Depends(get_container),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> WorkoutHistoryOutput:
    """Consultar histórico de treinos."""
    input_data = ViewWorkoutHistoryInput(
        athlete_profile_id=athlete_profile_id,
        user_id=current_user.user_id,
        limit=limit,
        offset=offset,
    )
    return await container.workout_use_cases().view_history(input_data)


@router.get("/suggestion", response_model=WorkoutSuggestionOutput)
async def get_next_suggestion(
    athlete_profile_id: UUID,
    current_user: TokenPayload = Depends(get_current_user),
    container: Container = Depends(get_container),
) -> WorkoutSuggestionOutput:
    """Obter sugestão do próximo treino."""
    input_data = GetNextWorkoutSuggestionInput(
        athlete_profile_id=athlete_profile_id,
        user_id=current_user.user_id,
    )
    return await container.workout_use_cases().get_next_suggestion(input_data)
