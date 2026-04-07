from __future__ import annotations

from collections.abc import Callable

from smart_pace.application.dtos.workout import (
    GetNextWorkoutSuggestionInput,
    LogWorkoutInput,
    ViewWorkoutHistoryInput,
    WorkoutHistoryOutput,
    WorkoutLogOutput,
    WorkoutSuggestionOutput,
)
from smart_pace.application.ports.clock import Clock
from smart_pace.application.ports.unit_of_work import UnitOfWork
from smart_pace.application.use_cases._helpers import (
    build_heart_rate_zones_output,
    build_workout_log_output,
    ensure_profile_ownership,
)
from smart_pace.domain.entities.athlete_profile import AthleteProfile
from smart_pace.domain.entities.performance_metrics import PerformanceMetrics
from smart_pace.domain.entities.workout_log import WorkoutLog
from smart_pace.domain.exceptions import (
    EntityNotFoundException,
    UnauthorizedException,
)
from smart_pace.domain.services.workout_suggestion_engine import (
    suggest_next_session_type,
)
from smart_pace.domain.value_objects.distance import Distance
from smart_pace.domain.value_objects.duration import Duration
from smart_pace.domain.value_objects.heart_rate import HeartRate


class WorkoutUseCases:
    def __init__(
        self,
        unit_of_work: Callable[[], UnitOfWork],
        clock: Clock,
    ) -> None:
        self.unit_of_work = unit_of_work
        self.clock = clock

    async def log_session(self, input_data: LogWorkoutInput) -> WorkoutLogOutput:
        """UC11 — Registrar sessão de treino."""
        async with self.unit_of_work() as uow:
            session = await uow.workout_sessions.find_by_id(
                input_data.workout_session_id
            )
            if session is None:
                raise EntityNotFoundException("Workout session not found")

            profile = await uow.athlete_profiles.find_by_id(
                input_data.athlete_profile_id
            )
            if profile is None:
                raise EntityNotFoundException("Athlete profile not found")

            ensure_profile_ownership(profile, input_data.user_id)

            if session.athlete_profile_id != input_data.athlete_profile_id:
                raise UnauthorizedException(
                    "Workout session does not belong to this athlete"
                )

            actual_distance = Distance(input_data.actual_distance_meters)
            actual_duration = Duration(input_data.actual_duration_seconds)
            average_heart_rate = (
                HeartRate(input_data.average_heart_rate)
                if input_data.average_heart_rate is not None
                else None
            )
            maximum_heart_rate = (
                HeartRate(input_data.maximum_heart_rate)
                if input_data.maximum_heart_rate is not None
                else None
            )

            workout_log = WorkoutLog.create_with_calculated_pace(
                workout_session_id=input_data.workout_session_id,
                athlete_profile_id=input_data.athlete_profile_id,
                started_at=input_data.started_at,
                finished_at=input_data.finished_at,
                actual_distance=actual_distance,
                actual_duration=actual_duration,
                average_heart_rate=average_heart_rate,
                maximum_heart_rate=maximum_heart_rate,
                perceived_exertion=input_data.perceived_exertion,
                notes=input_data.notes,
            )

            session.mark_completed()
            await uow.workout_sessions.save(session)
            await uow.workout_logs.save(workout_log)

            # Recalcula métricas de performance dentro da mesma transação
            await _recalculate_performance_metrics(uow, profile, self.clock)

            await uow.commit()

        return build_workout_log_output(workout_log)

    async def view_history(
        self, input_data: ViewWorkoutHistoryInput
    ) -> WorkoutHistoryOutput:
        """UC12 — Consultar histórico de treinos."""
        async with self.unit_of_work() as uow:
            profile = await uow.athlete_profiles.find_by_id(
                input_data.athlete_profile_id
            )
            if profile is None:
                raise EntityNotFoundException("Athlete profile not found")

            ensure_profile_ownership(profile, input_data.user_id)

            logs = await uow.workout_logs.find_by_athlete_profile_id(
                input_data.athlete_profile_id,
                limit=input_data.limit,
                offset=input_data.offset,
            )

        return WorkoutHistoryOutput(
            logs=[build_workout_log_output(log) for log in logs],
            total_returned=len(logs),
        )

    async def get_next_suggestion(
        self, input_data: GetNextWorkoutSuggestionInput
    ) -> WorkoutSuggestionOutput:
        """UC13 — Obter sugestão do próximo treino."""
        async with self.unit_of_work() as uow:
            profile = await uow.athlete_profiles.find_by_id(
                input_data.athlete_profile_id
            )
            if profile is None:
                raise EntityNotFoundException("Athlete profile not found")

            ensure_profile_ownership(profile, input_data.user_id)

            recent_sessions = await uow.workout_sessions.find_by_athlete_profile_id(
                input_data.athlete_profile_id, limit=5
            )

        suggested_type = suggest_next_session_type(profile, recent_sessions)
        return WorkoutSuggestionOutput(suggested_session_type=suggested_type)


async def _recalculate_performance_metrics(
    uow: UnitOfWork,
    profile: AthleteProfile,
    clock: Clock,
) -> None:
    """Cria novo snapshot de métricas de performance.

    Roda dentro da transação aberta pelo use case (não chama commit).
    MVP: mantém CTL/ATL existentes ou zero se for o primeiro registro.
    """
    latest = await uow.performance_metrics.find_latest_by_athlete_profile_id(profile.id)

    zones_output = build_heart_rate_zones_output(profile)
    # Converte de volta para HeartRateZone do domínio
    from smart_pace.domain.value_objects.heart_rate import HeartRateZone

    heart_rate_zones = [
        HeartRateZone(name=zone.name, min_bpm=zone.min_bpm, max_bpm=zone.max_bpm)
        for zone in zones_output
    ]

    now = clock.now()

    if latest is not None:
        estimated_vo2max = latest.estimated_vo2max
        chronic_training_load = latest.chronic_training_load
        acute_training_load = latest.acute_training_load
        lactate_threshold_pace = latest.lactate_threshold_pace
    else:
        from smart_pace.domain.value_objects.vo2max import Vo2max

        estimated_vo2max = (
            profile.current_vo2max if profile.current_vo2max else Vo2max(30.0)
        )
        chronic_training_load = 0.0
        acute_training_load = 0.0
        lactate_threshold_pace = None

    metrics = PerformanceMetrics(
        athlete_profile_id=profile.id,
        calculated_at=now,
        estimated_vo2max=estimated_vo2max,
        heart_rate_zones=heart_rate_zones,
        lactate_threshold_pace=lactate_threshold_pace,
        chronic_training_load=chronic_training_load,
        acute_training_load=acute_training_load,
    )
    await uow.performance_metrics.save(metrics)
