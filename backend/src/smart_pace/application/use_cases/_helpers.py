from __future__ import annotations

from uuid import UUID

from smart_pace.application.dtos.profile import HeartRateZoneOutput
from smart_pace.domain.entities.athlete_profile import AthleteProfile
from smart_pace.domain.exceptions import UnauthorizedException
from smart_pace.domain.services.training_zone_calculator import (
    compute_heart_rate_zones,
)


def ensure_profile_ownership(profile: AthleteProfile, user_id: UUID) -> None:
    """Verifica se o perfil pertence ao usuário informado."""
    if profile.user_id != user_id:
        raise UnauthorizedException("User does not own this athlete profile")


def build_heart_rate_zones_output(
    profile: AthleteProfile,
) -> list[HeartRateZoneOutput]:
    """Calcula zonas de FC e converte para DTOs de saída."""
    zones = compute_heart_rate_zones(
        profile.maximum_heart_rate, profile.resting_heart_rate
    )
    return [
        HeartRateZoneOutput(name=zone.name, min_bpm=zone.min_bpm, max_bpm=zone.max_bpm)
        for zone in zones
    ]
