from __future__ import annotations

from collections.abc import Callable

from smart_pace.application.dtos.training_plan import (
    ActivateTrainingPlanInput,
    CancelTrainingPlanInput,
    CreateTrainingPlanInput,
    TrainingPlanOutput,
)
from smart_pace.application.ports.unit_of_work import UnitOfWork
from smart_pace.application.use_cases._helpers import ensure_profile_ownership
from smart_pace.domain.entities.training_plan import TrainingPlan
from smart_pace.domain.exceptions import EntityNotFoundException


class TrainingUseCases:
    def __init__(self, unit_of_work: Callable[[], UnitOfWork]) -> None:
        self.unit_of_work = unit_of_work

    async def create_plan(
        self, input_data: CreateTrainingPlanInput
    ) -> TrainingPlanOutput:
        """UC8 — Criar plano de treino."""
        async with self.unit_of_work() as uow:
            profile = await uow.athlete_profiles.find_by_id(
                input_data.athlete_profile_id
            )
            if profile is None:
                raise EntityNotFoundException("Athlete profile not found")

            ensure_profile_ownership(profile, input_data.user_id)

            plan = TrainingPlan(
                athlete_profile_id=input_data.athlete_profile_id,
                name=input_data.name,
                goal_description=input_data.goal_description,
                start_date=input_data.start_date,
                end_date=input_data.end_date,
                sport_type=input_data.sport_type,
            )
            await uow.training_plans.save(plan)
            await uow.commit()

        return _build_training_plan_output(plan)

    async def activate_plan(
        self, input_data: ActivateTrainingPlanInput
    ) -> TrainingPlanOutput:
        """UC9 — Ativar plano."""
        async with self.unit_of_work() as uow:
            plan = await uow.training_plans.find_by_id(input_data.plan_id)
            if plan is None:
                raise EntityNotFoundException("Training plan not found")

            profile = await uow.athlete_profiles.find_by_id(plan.athlete_profile_id)
            if profile is None:
                raise EntityNotFoundException("Athlete profile not found")

            ensure_profile_ownership(profile, input_data.user_id)

            plan.activate()
            await uow.training_plans.save(plan)
            await uow.commit()

        return _build_training_plan_output(plan)

    async def cancel_plan(
        self, input_data: CancelTrainingPlanInput
    ) -> TrainingPlanOutput:
        """UC10 — Cancelar plano."""
        async with self.unit_of_work() as uow:
            plan = await uow.training_plans.find_by_id(input_data.plan_id)
            if plan is None:
                raise EntityNotFoundException("Training plan not found")

            profile = await uow.athlete_profiles.find_by_id(plan.athlete_profile_id)
            if profile is None:
                raise EntityNotFoundException("Athlete profile not found")

            ensure_profile_ownership(profile, input_data.user_id)

            plan.cancel()
            await uow.training_plans.save(plan)
            await uow.commit()

        return _build_training_plan_output(plan)


def _build_training_plan_output(plan: TrainingPlan) -> TrainingPlanOutput:
    """Mapeia entidade TrainingPlan para DTO de saída."""
    return TrainingPlanOutput(
        id=plan.id,
        athlete_profile_id=plan.athlete_profile_id,
        name=plan.name,
        goal_description=plan.goal_description,
        start_date=plan.start_date,
        end_date=plan.end_date,
        sport_type=plan.sport_type,
        status=plan.status,
        duration_in_weeks=plan.duration_in_weeks(),
    )
