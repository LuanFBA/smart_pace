from __future__ import annotations

from uuid import UUID

from smart_pace.application.dtos.profile import (
    AthleteProfileOutput,
    HeartRateZoneOutput,
)
from smart_pace.application.dtos.workout import WorkoutLogOutput
from smart_pace.domain.entities.athlete_profile import AthleteProfile
from smart_pace.domain.entities.workout_log import WorkoutLog
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


def build_athlete_profile_output(
    profile: AthleteProfile, zones: list[HeartRateZoneOutput]
) -> AthleteProfileOutput:
    """Mapeia entidade AthleteProfile para DTO de saída."""
    return AthleteProfileOutput(
        id=profile.id,
        user_id=profile.user_id,
        sport_type=profile.sport_type,
        date_of_birth=profile.date_of_birth,
        resting_heart_rate=profile.resting_heart_rate.beats_per_minute,
        maximum_heart_rate=profile.maximum_heart_rate.beats_per_minute,
        functional_threshold_power=profile.functional_threshold_power,
        current_vo2max=(
            profile.current_vo2max.value if profile.current_vo2max else None
        ),
        training_experience_years=profile.training_experience_years,
        weekly_target_hours=profile.weekly_target_hours,
        heart_rate_zones=zones,
    )


def build_workout_log_output(log: WorkoutLog) -> WorkoutLogOutput:
    """Mapeia entidade WorkoutLog para DTO de saída."""
    return WorkoutLogOutput(
        id=log.id,
        workout_session_id=log.workout_session_id,
        athlete_profile_id=log.athlete_profile_id,
        started_at=log.started_at,
        finished_at=log.finished_at,
        actual_distance_meters=log.actual_distance.meters,
        actual_duration_seconds=log.actual_duration.seconds,
        average_pace_seconds_per_km=log.average_pace.seconds_per_kilometer,
        average_heart_rate=(
            log.average_heart_rate.beats_per_minute if log.average_heart_rate else None
        ),
        maximum_heart_rate=(
            log.maximum_heart_rate.beats_per_minute if log.maximum_heart_rate else None
        ),
        perceived_exertion=log.perceived_exertion,
        notes=log.notes,
    )
