from __future__ import annotations

from collections.abc import Callable
from datetime import timedelta

from smart_pace.application.dtos.workout import (
    DeleteWorkoutLogInput,
    GetNextWorkoutSuggestionInput,
    GetWorkoutLogInput,
    LogWorkoutInput,
    ScheduleWorkoutSessionInput,
    UpdateWorkoutLogInput,
    ViewWorkoutHistoryInput,
    WorkoutHistoryOutput,
    WorkoutLogOutput,
    WorkoutSessionOutput,
    WorkoutSuggestionOutput,
)
from smart_pace.application.ports.clock import Clock
from smart_pace.application.ports.unit_of_work import UnitOfWork
from smart_pace.application.use_cases._helpers import (
    build_heart_rate_zones_output,
    ensure_profile_ownership,
)
from smart_pace.domain.entities.athlete_profile import AthleteProfile
from smart_pace.domain.entities.performance_metrics import PerformanceMetrics
from smart_pace.domain.entities.workout_log import WorkoutLog
from smart_pace.domain.entities.workout_session import WorkoutSession
from smart_pace.domain.enums import SessionType
from smart_pace.domain.exceptions import (
    EntityNotFoundException,
    UnauthorizedException,
)
from smart_pace.domain.services.workout_suggestion_engine import (
    suggest_next_session_type,
)
from smart_pace.domain.value_objects.distance import Distance
from smart_pace.domain.value_objects.duration import Duration
from smart_pace.domain.value_objects.heart_rate import HeartRate, HeartRateZone
from smart_pace.domain.value_objects.pace import Pace
from smart_pace.domain.value_objects.vo2max import Vo2max


class WorkoutUseCases:
    def __init__(
        self,
        unit_of_work: Callable[[], UnitOfWork],
        clock: Clock,
    ) -> None:
        self.unit_of_work = unit_of_work
        self.clock = clock

    async def schedule_session(
        self, input_data: ScheduleWorkoutSessionInput
    ) -> WorkoutSessionOutput:
        """UC16 — Agendar sessão de treino manualmente."""
        async with self.unit_of_work() as uow:
            profile = await uow.athlete_profiles.find_by_id(
                input_data.athlete_profile_id
            )
            if profile is None:
                raise EntityNotFoundException("Athlete profile not found")

            ensure_profile_ownership(profile, input_data.user_id)

            target_distance = (
                Distance(input_data.target_distance_meters)
                if input_data.target_distance_meters is not None
                else None
            )
            target_duration = (
                Duration(input_data.target_duration_seconds)
                if input_data.target_duration_seconds is not None
                else None
            )
            target_min_pace = (
                Pace(input_data.target_min_pace_seconds_per_km)
                if input_data.target_min_pace_seconds_per_km is not None
                else None
            )
            target_max_pace = (
                Pace(input_data.target_max_pace_seconds_per_km)
                if input_data.target_max_pace_seconds_per_km is not None
                else None
            )

            session = WorkoutSession(
                athlete_profile_id=input_data.athlete_profile_id,
                scheduled_date=input_data.scheduled_date,
                session_type=SessionType(input_data.session_type),
                target_distance=target_distance,
                target_duration=target_duration,
                target_min_pace=target_min_pace,
                target_max_pace=target_max_pace,
            )
            await uow.workout_sessions.save(session)
            await uow.commit()

        return _build_workout_session_output(session)

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
                average_power_watts=input_data.average_power_watts,
            )

            session.mark_completed()
            await uow.workout_sessions.save(session)
            await uow.workout_logs.save(workout_log)

            # Recalcula métricas de performance dentro da mesma transação
            await self._recalculate_performance_metrics(uow, profile)

            await uow.commit()

        return _build_workout_log_output(workout_log, session.session_type.value)

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
            total_count = await uow.workout_logs.count_by_athlete_profile_id(
                input_data.athlete_profile_id
            )

            # Carrega o session_type de cada log com cache por sessão
            # para evitar buscas repetidas quando houver múltiplos logs da mesma sessão
            session_type_cache: dict = {}
            outputs: list[WorkoutLogOutput] = []
            for log in logs:
                session_type = session_type_cache.get(log.workout_session_id)
                if session_type is None:
                    session = await uow.workout_sessions.find_by_id(
                        log.workout_session_id
                    )
                    session_type = session.session_type.value if session else "easy_run"
                    session_type_cache[log.workout_session_id] = session_type
                outputs.append(_build_workout_log_output(log, session_type))

        return WorkoutHistoryOutput(
            logs=outputs,
            total_returned=len(logs),
            total_count=total_count,
        )

    async def get_workout_log(self, input_data: GetWorkoutLogInput) -> WorkoutLogOutput:
        """Busca log individual por ID com validação de ownership."""
        async with self.unit_of_work() as uow:
            log = await uow.workout_logs.find_by_id(input_data.log_id)
            if log is None:
                raise EntityNotFoundException("Workout log not found")

            profile = await uow.athlete_profiles.find_by_id(log.athlete_profile_id)
            if profile is None:
                raise EntityNotFoundException("Athlete profile not found")

            ensure_profile_ownership(profile, input_data.user_id)

            session = await uow.workout_sessions.find_by_id(log.workout_session_id)
            session_type = session.session_type.value if session else "easy_run"

        return _build_workout_log_output(log, session_type)

    async def update_workout_log(self, input_data: UpdateWorkoutLogInput) -> WorkoutLogOutput:
        """Substitui todos os campos editáveis do log, recalculando pace."""
        async with self.unit_of_work() as uow:
            existing = await uow.workout_logs.find_by_id(input_data.log_id)
            if existing is None:
                raise EntityNotFoundException("Workout log not found")

            profile = await uow.athlete_profiles.find_by_id(existing.athlete_profile_id)
            if profile is None:
                raise EntityNotFoundException("Athlete profile not found")

            ensure_profile_ownership(profile, input_data.user_id)

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

            updated_log = WorkoutLog.create_with_calculated_pace(
                workout_session_id=existing.workout_session_id,
                athlete_profile_id=existing.athlete_profile_id,
                started_at=input_data.started_at,
                finished_at=input_data.finished_at,
                actual_distance=Distance(input_data.actual_distance_meters),
                actual_duration=Duration(input_data.actual_duration_seconds),
                average_heart_rate=average_heart_rate,
                maximum_heart_rate=maximum_heart_rate,
                perceived_exertion=input_data.perceived_exertion,
                notes=input_data.notes,
                average_power_watts=input_data.average_power_watts,
            )
            # Preserva o id original para que o save faça UPDATE e não INSERT
            updated_log.id = existing.id

            await uow.workout_logs.save(updated_log)
            await self._recalculate_performance_metrics(uow, profile)
            await uow.commit()

            session = await uow.workout_sessions.find_by_id(existing.workout_session_id)
            session_type = session.session_type.value if session else "easy_run"

        return _build_workout_log_output(updated_log, session_type)

    async def delete_workout_log(self, input_data: DeleteWorkoutLogInput) -> None:
        """Remove log e reverte sessão associada para scheduled."""
        async with self.unit_of_work() as uow:
            log = await uow.workout_logs.find_by_id(input_data.log_id)
            if log is None:
                raise EntityNotFoundException("Workout log not found")

            profile = await uow.athlete_profiles.find_by_id(log.athlete_profile_id)
            if profile is None:
                raise EntityNotFoundException("Athlete profile not found")

            ensure_profile_ownership(profile, input_data.user_id)

            session = await uow.workout_sessions.find_by_id(log.workout_session_id)
            if session is not None:
                session.revert_to_scheduled()
                await uow.workout_sessions.save(session)

            await uow.workout_logs.delete(log.id)
            await self._recalculate_performance_metrics(uow, profile)
            await uow.commit()

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
        return WorkoutSuggestionOutput(suggested_session_type=suggested_type.value)

    async def _recalculate_performance_metrics(
        self,
        uow: UnitOfWork,
        profile: AthleteProfile,
    ) -> None:
        """Cria novo snapshot de métricas de performance com EWMA real.

        CTL (fitness): EWMA de 42 dias — α = 2/(42+1) ≈ 0.046
        ATL (fadiga):  EWMA de 7 dias  — α = 2/(7+1)  = 0.25
        Carga por sessão: RPE × duração_em_minutos (TSS simplificado).
        RPE padrão = 5 quando não informado.

        Roda dentro da transação aberta pelo use case (não chama commit).
        """
        now = self.clock.now()
        today = now.date()
        since = today - timedelta(days=41)  # janela de 42 dias (inclusive)

        recent_logs = await uow.workout_logs.find_since_date(profile.id, since)

        # Agrupa carga de treino por dia
        tl_by_date: dict = {}
        for log in recent_logs:
            log_date = log.started_at.date()
            rpe = log.perceived_exertion if log.perceived_exertion is not None else 5
            duration_minutes = log.actual_duration.seconds / 60
            tl_by_date[log_date] = tl_by_date.get(log_date, 0.0) + rpe * duration_minutes

        # EWMA dia a dia sobre os últimos 42 dias
        alpha_ctl = 2 / (42 + 1)
        alpha_atl = 2 / (7 + 1)
        ctl = 0.0
        atl = 0.0
        for offset in range(42):
            day = since + timedelta(days=offset)
            tl_day = tl_by_date.get(day, 0.0)
            ctl = ctl * (1 - alpha_ctl) + tl_day * alpha_ctl
            atl = atl * (1 - alpha_atl) + tl_day * alpha_atl

        latest = await uow.performance_metrics.find_latest_by_athlete_profile_id(
            profile.id
        )

        if latest is not None:
            estimated_vo2max = latest.estimated_vo2max
            lactate_threshold_pace = latest.lactate_threshold_pace
        else:
            estimated_vo2max = (
                profile.current_vo2max if profile.current_vo2max else Vo2max(30.0)
            )
            lactate_threshold_pace = None

        zones_output = build_heart_rate_zones_output(profile)
        heart_rate_zones = [
            HeartRateZone(name=zone.name, min_bpm=zone.min_bpm, max_bpm=zone.max_bpm)
            for zone in zones_output
        ]

        metrics = PerformanceMetrics(
            athlete_profile_id=profile.id,
            calculated_at=now,
            estimated_vo2max=estimated_vo2max,
            heart_rate_zones=heart_rate_zones,
            lactate_threshold_pace=lactate_threshold_pace,
            chronic_training_load=round(ctl, 2),
            acute_training_load=round(atl, 2),
        )
        await uow.performance_metrics.save(metrics)


def _build_workout_session_output(session: WorkoutSession) -> WorkoutSessionOutput:
    """Mapeia entidade WorkoutSession para DTO de saída."""
    return WorkoutSessionOutput(
        id=session.id,
        athlete_profile_id=session.athlete_profile_id,
        training_block_id=session.training_block_id,
        scheduled_date=session.scheduled_date,
        session_type=session.session_type.value,
        status=session.status.value,
        target_distance_meters=(
            session.target_distance.meters if session.target_distance else None
        ),
        target_duration_seconds=(
            session.target_duration.seconds if session.target_duration else None
        ),
        target_min_pace_seconds_per_km=(
            session.target_min_pace.seconds_per_kilometer
            if session.target_min_pace
            else None
        ),
        target_max_pace_seconds_per_km=(
            session.target_max_pace.seconds_per_kilometer
            if session.target_max_pace
            else None
        ),
    )


def _build_workout_log_output(log: WorkoutLog, session_type: str) -> WorkoutLogOutput:
    """Mapeia entidade WorkoutLog para DTO de saída."""
    return WorkoutLogOutput(
        id=log.id,
        workout_session_id=log.workout_session_id,
        athlete_profile_id=log.athlete_profile_id,
        session_type=session_type,
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
        average_power_watts=log.average_power_watts,
    )
