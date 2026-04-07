from __future__ import annotations

from collections.abc import Callable

from smart_pace.application.dtos.metrics import (
    PerformanceDashboardOutput,
    ViewPerformanceDashboardInput,
)
from smart_pace.application.ports.unit_of_work import UnitOfWork
from smart_pace.application.use_cases._helpers import (
    build_heart_rate_zones_output,
    ensure_profile_ownership,
)
from smart_pace.domain.exceptions import EntityNotFoundException


class MetricsUseCases:
    def __init__(self, unit_of_work: Callable[[], UnitOfWork]) -> None:
        self.unit_of_work = unit_of_work

    async def view_dashboard(
        self, input_data: ViewPerformanceDashboardInput
    ) -> PerformanceDashboardOutput:
        """UC14 — Ver dashboard de evolução."""
        async with self.unit_of_work() as uow:
            profile = await uow.athlete_profiles.find_by_id(
                input_data.athlete_profile_id
            )
            if profile is None:
                raise EntityNotFoundException("Athlete profile not found")

            ensure_profile_ownership(profile, input_data.user_id)

            metrics = await uow.performance_metrics.find_latest_by_athlete_profile_id(
                input_data.athlete_profile_id
            )

        # Se não houver métricas, retorna dashboard vazio com zonas do perfil
        zones = build_heart_rate_zones_output(profile)

        if metrics is None:
            return PerformanceDashboardOutput(
                athlete_profile_id=profile.id,
                calculated_at=None,
                estimated_vo2max=None,
                heart_rate_zones=zones,
                lactate_threshold_pace_seconds_per_km=None,
                chronic_training_load=0.0,
                acute_training_load=0.0,
                training_stress_balance=0.0,
                fitness_fatigue_ratio=None,
            )

        return PerformanceDashboardOutput(
            athlete_profile_id=profile.id,
            calculated_at=metrics.calculated_at,
            estimated_vo2max=metrics.estimated_vo2max.value,
            heart_rate_zones=zones,
            lactate_threshold_pace_seconds_per_km=(
                metrics.lactate_threshold_pace.seconds_per_kilometer
                if metrics.lactate_threshold_pace
                else None
            ),
            chronic_training_load=metrics.chronic_training_load,
            acute_training_load=metrics.acute_training_load,
            training_stress_balance=metrics.training_stress_balance,
            fitness_fatigue_ratio=metrics.fitness_fatigue_ratio,
        )
