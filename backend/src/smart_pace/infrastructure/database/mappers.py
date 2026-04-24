"""Conversão explícita entre modelos ORM e entidades de domínio.

Regra: nenhum modelo ORM vaza para fora da camada de infraestrutura.
"""

from __future__ import annotations

from smart_pace.domain.entities.athlete_profile import AthleteProfile
from smart_pace.domain.entities.performance_metrics import PerformanceMetrics
from smart_pace.domain.entities.training_block import TrainingBlock
from smart_pace.domain.entities.training_plan import TrainingPlan
from smart_pace.domain.entities.user import User
from smart_pace.domain.entities.workout_log import WorkoutLog
from smart_pace.domain.entities.workout_session import WorkoutSession
from smart_pace.domain.enums import (
    SessionStatus,
    SessionType,
    SportType,
    TrainingPhase,
    TrainingPlanStatus,
)
from smart_pace.domain.value_objects.distance import Distance
from smart_pace.domain.value_objects.duration import Duration
from smart_pace.domain.value_objects.email_address import EmailAddress
from smart_pace.domain.value_objects.heart_rate import HeartRate, HeartRateZone
from smart_pace.domain.value_objects.pace import Pace
from smart_pace.domain.value_objects.vo2max import Vo2max
from smart_pace.infrastructure.database.models import (
    AthleteProfileModel,
    PerformanceMetricsModel,
    TrainingBlockModel,
    TrainingPlanModel,
    UserModel,
    WorkoutLogModel,
    WorkoutSessionModel,
)


# ──────────────────────────────────────────
# User
# ──────────────────────────────────────────


def user_model_to_entity(model: UserModel) -> User:
    return User(
        email=EmailAddress(model.email),
        password_hash=model.password_hash,
        full_name=model.full_name,
        id=model.id,
        is_active=model.is_active,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def user_entity_to_model(entity: User) -> UserModel:
    return UserModel(
        id=entity.id,
        email=entity.email.value,
        password_hash=entity.password_hash,
        full_name=entity.full_name,
        is_active=entity.is_active,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )


# ──────────────────────────────────────────
# AthleteProfile
# ──────────────────────────────────────────


def athlete_profile_model_to_entity(model: AthleteProfileModel) -> AthleteProfile:
    return AthleteProfile(
        user_id=model.user_id,
        sport_type=SportType(model.sport_type),
        date_of_birth=model.date_of_birth,
        resting_heart_rate=HeartRate(model.resting_heart_rate_bpm),
        maximum_heart_rate=HeartRate(model.maximum_heart_rate_bpm),
        id=model.id,
        functional_threshold_power=model.functional_threshold_power,
        current_vo2max=Vo2max(model.current_vo2max) if model.current_vo2max is not None else None,
        training_experience_years=model.training_experience_years,
        weekly_target_hours=model.weekly_target_hours,
    )


def athlete_profile_entity_to_model(entity: AthleteProfile) -> AthleteProfileModel:
    return AthleteProfileModel(
        id=entity.id,
        user_id=entity.user_id,
        sport_type=entity.sport_type.value,
        date_of_birth=entity.date_of_birth,
        resting_heart_rate_bpm=entity.resting_heart_rate.beats_per_minute,
        maximum_heart_rate_bpm=entity.maximum_heart_rate.beats_per_minute,
        functional_threshold_power=entity.functional_threshold_power,
        current_vo2max=entity.current_vo2max.value if entity.current_vo2max else None,
        training_experience_years=entity.training_experience_years,
        weekly_target_hours=entity.weekly_target_hours,
    )


# ──────────────────────────────────────────
# TrainingPlan
# ──────────────────────────────────────────


def training_plan_model_to_entity(model: TrainingPlanModel) -> TrainingPlan:
    return TrainingPlan(
        athlete_profile_id=model.athlete_profile_id,
        name=model.name,
        goal_description=model.goal_description,
        start_date=model.start_date,
        end_date=model.end_date,
        sport_type=SportType(model.sport_type),
        id=model.id,
        status=TrainingPlanStatus(model.status),
    )


def training_plan_entity_to_model(entity: TrainingPlan) -> TrainingPlanModel:
    return TrainingPlanModel(
        id=entity.id,
        athlete_profile_id=entity.athlete_profile_id,
        name=entity.name,
        goal_description=entity.goal_description,
        start_date=entity.start_date,
        end_date=entity.end_date,
        sport_type=entity.sport_type.value,
        status=entity.status.value,
    )


# ──────────────────────────────────────────
# TrainingBlock
# ──────────────────────────────────────────


def training_block_model_to_entity(model: TrainingBlockModel) -> TrainingBlock:
    return TrainingBlock(
        training_plan_id=model.training_plan_id,
        week_number=model.week_number,
        phase=TrainingPhase(model.phase),
        target_weekly_distance=Distance(model.target_weekly_distance_meters),
        target_weekly_duration=Duration(model.target_weekly_duration_seconds),
        id=model.id,
    )


def training_block_entity_to_model(entity: TrainingBlock) -> TrainingBlockModel:
    return TrainingBlockModel(
        id=entity.id,
        training_plan_id=entity.training_plan_id,
        week_number=entity.week_number,
        phase=entity.phase.value,
        target_weekly_distance_meters=entity.target_weekly_distance.meters,
        target_weekly_duration_seconds=entity.target_weekly_duration.seconds,
    )


# ──────────────────────────────────────────
# WorkoutSession
# ──────────────────────────────────────────


def workout_session_model_to_entity(model: WorkoutSessionModel) -> WorkoutSession:
    target_hr_zone: HeartRateZone | None = None
    if model.target_heart_rate_zone is not None:
        z = model.target_heart_rate_zone
        target_hr_zone = HeartRateZone(
            name=z["name"], min_bpm=z["min_bpm"], max_bpm=z["max_bpm"]
        )

    return WorkoutSession(
        athlete_profile_id=model.athlete_profile_id,
        scheduled_date=model.scheduled_date,
        session_type=SessionType(model.session_type),
        id=model.id,
        training_block_id=model.training_block_id,
        target_distance=(
            Distance(model.target_distance_meters)
            if model.target_distance_meters is not None
            else None
        ),
        target_duration=(
            Duration(model.target_duration_seconds)
            if model.target_duration_seconds is not None
            else None
        ),
        target_min_pace=(
            Pace(model.target_min_pace_sec_per_km)
            if model.target_min_pace_sec_per_km is not None
            else None
        ),
        target_max_pace=(
            Pace(model.target_max_pace_sec_per_km)
            if model.target_max_pace_sec_per_km is not None
            else None
        ),
        target_heart_rate_zone=target_hr_zone,
        status=SessionStatus(model.status),
    )


def workout_session_entity_to_model(entity: WorkoutSession) -> WorkoutSessionModel:
    hr_zone_json: dict[str, object] | None = None
    if entity.target_heart_rate_zone is not None:
        z = entity.target_heart_rate_zone
        hr_zone_json = {"name": z.name, "min_bpm": z.min_bpm, "max_bpm": z.max_bpm}

    return WorkoutSessionModel(
        id=entity.id,
        athlete_profile_id=entity.athlete_profile_id,
        scheduled_date=entity.scheduled_date,
        session_type=entity.session_type.value,
        training_block_id=entity.training_block_id,
        target_distance_meters=(
            entity.target_distance.meters if entity.target_distance else None
        ),
        target_duration_seconds=(
            entity.target_duration.seconds if entity.target_duration else None
        ),
        target_min_pace_sec_per_km=(
            entity.target_min_pace.seconds_per_kilometer
            if entity.target_min_pace
            else None
        ),
        target_max_pace_sec_per_km=(
            entity.target_max_pace.seconds_per_kilometer
            if entity.target_max_pace
            else None
        ),
        target_heart_rate_zone=hr_zone_json,
        status=entity.status.value,
    )


# ──────────────────────────────────────────
# WorkoutLog
# ──────────────────────────────────────────


def workout_log_model_to_entity(model: WorkoutLogModel) -> WorkoutLog:
    return WorkoutLog(
        workout_session_id=model.workout_session_id,
        athlete_profile_id=model.athlete_profile_id,
        started_at=model.started_at,
        finished_at=model.finished_at,
        actual_distance=Distance(model.actual_distance_meters),
        actual_duration=Duration(model.actual_duration_seconds),
        average_pace=Pace(model.average_pace_sec_per_km),
        id=model.id,
        average_heart_rate=(
            HeartRate(model.average_heart_rate_bpm)
            if model.average_heart_rate_bpm is not None
            else None
        ),
        maximum_heart_rate=(
            HeartRate(model.maximum_heart_rate_bpm)
            if model.maximum_heart_rate_bpm is not None
            else None
        ),
        perceived_exertion=model.perceived_exertion,
        notes=model.notes,
        average_power_watts=model.average_power_watts,
    )


def workout_log_entity_to_model(entity: WorkoutLog) -> WorkoutLogModel:
    return WorkoutLogModel(
        id=entity.id,
        workout_session_id=entity.workout_session_id,
        athlete_profile_id=entity.athlete_profile_id,
        started_at=entity.started_at,
        finished_at=entity.finished_at,
        actual_distance_meters=entity.actual_distance.meters,
        actual_duration_seconds=entity.actual_duration.seconds,
        average_pace_sec_per_km=entity.average_pace.seconds_per_kilometer,
        average_heart_rate_bpm=(
            entity.average_heart_rate.beats_per_minute
            if entity.average_heart_rate
            else None
        ),
        maximum_heart_rate_bpm=(
            entity.maximum_heart_rate.beats_per_minute
            if entity.maximum_heart_rate
            else None
        ),
        perceived_exertion=entity.perceived_exertion,
        notes=entity.notes,
        average_power_watts=entity.average_power_watts,
    )


# ──────────────────────────────────────────
# PerformanceMetrics
# ──────────────────────────────────────────


def performance_metrics_model_to_entity(
    model: PerformanceMetricsModel,
) -> PerformanceMetrics:
    zones = [
        HeartRateZone(name=z["name"], min_bpm=z["min_bpm"], max_bpm=z["max_bpm"])
        for z in model.heart_rate_zones
    ]
    return PerformanceMetrics(
        athlete_profile_id=model.athlete_profile_id,
        calculated_at=model.calculated_at,
        estimated_vo2max=Vo2max(model.estimated_vo2max),
        heart_rate_zones=zones,
        id=model.id,
        lactate_threshold_pace=(
            Pace(model.lactate_threshold_pace_sec_per_km)
            if model.lactate_threshold_pace_sec_per_km is not None
            else None
        ),
        chronic_training_load=model.chronic_training_load,
        acute_training_load=model.acute_training_load,
    )


def performance_metrics_entity_to_model(
    entity: PerformanceMetrics,
) -> PerformanceMetricsModel:
    zones_json = [
        {"name": z.name, "min_bpm": z.min_bpm, "max_bpm": z.max_bpm}
        for z in entity.heart_rate_zones
    ]
    return PerformanceMetricsModel(
        id=entity.id,
        athlete_profile_id=entity.athlete_profile_id,
        calculated_at=entity.calculated_at,
        estimated_vo2max=entity.estimated_vo2max.value,
        heart_rate_zones=zones_json,
        lactate_threshold_pace_sec_per_km=(
            entity.lactate_threshold_pace.seconds_per_kilometer
            if entity.lactate_threshold_pace
            else None
        ),
        chronic_training_load=entity.chronic_training_load,
        acute_training_load=entity.acute_training_load,
    )
