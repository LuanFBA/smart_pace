"""Rotas de perfis de atleta."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status

from smart_pace.application.dtos.profile import (
    AthleteProfileOutput,
    CreateAthleteProfileInput,
    GetProfileByUserIdInput,
    HeartRateZoneOutput,
    MyProfileOutput,
    UpdateHeartRateDataInput,
    ViewHeartRateZonesInput,
)
from smart_pace.application.ports.token_service import TokenPayload
from smart_pace.infrastructure.container import Container
from smart_pace.interface.dependencies import get_container, get_current_user
from smart_pace.interface.api.schemas.schemas import CreateAthleteProfileRequest, UpdateHeartRateRequest

router = APIRouter(prefix="/profiles", tags=["Perfis de Atleta"])


@router.post(
    "/",
    response_model=AthleteProfileOutput,
    status_code=status.HTTP_201_CREATED,
)
async def create_profile(
    body: CreateAthleteProfileRequest,
    current_user: TokenPayload = Depends(get_current_user),
    container: Container = Depends(get_container),
) -> AthleteProfileOutput:
    """Criar perfil de atleta."""
    input_data = CreateAthleteProfileInput(
        user_id=current_user.user_id,
        sport_type=body.sport_type,
        date_of_birth=body.date_of_birth,
        resting_heart_rate=body.resting_heart_rate,
        maximum_heart_rate=body.maximum_heart_rate,
        functional_threshold_power=body.functional_threshold_power,
        current_vo2max=body.current_vo2max,
        training_experience_years=body.training_experience_years,
        weekly_target_hours=body.weekly_target_hours,
    )
    return await container.profile_use_cases().create_profile(input_data)


@router.get("/me", response_model=MyProfileOutput)
async def get_my_profile(
    current_user: TokenPayload = Depends(get_current_user),
    container: Container = Depends(get_container),
) -> MyProfileOutput:
    """Consultar perfil do atleta autenticado, incluindo nome do usuário."""
    input_data = GetProfileByUserIdInput(user_id=current_user.user_id)
    return await container.profile_use_cases().get_my_profile(input_data)


@router.patch(
    "/{athlete_profile_id}/heart-rate",
    response_model=AthleteProfileOutput,
)
async def update_heart_rate(
    athlete_profile_id: UUID,
    body: UpdateHeartRateRequest,
    current_user: TokenPayload = Depends(get_current_user),
    container: Container = Depends(get_container),
) -> AthleteProfileOutput:
    """Atualizar dados de frequência cardíaca."""
    input_data = UpdateHeartRateDataInput(
        athlete_profile_id=athlete_profile_id,
        user_id=current_user.user_id,
        resting_heart_rate=body.resting_heart_rate,
        maximum_heart_rate=body.maximum_heart_rate,
    )
    return await container.profile_use_cases().update_heart_rate(input_data)


@router.get(
    "/{athlete_profile_id}/heart-rate-zones",
    response_model=list[HeartRateZoneOutput],
)
async def get_heart_rate_zones(
    athlete_profile_id: UUID,
    current_user: TokenPayload = Depends(get_current_user),
    container: Container = Depends(get_container),
) -> list[HeartRateZoneOutput]:
    """Consultar zonas de frequência cardíaca."""
    input_data = ViewHeartRateZonesInput(
        athlete_profile_id=athlete_profile_id,
        user_id=current_user.user_id,
    )
    return await container.profile_use_cases().view_heart_rate_zones(input_data)
