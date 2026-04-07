from __future__ import annotations

from collections.abc import Callable

from smart_pace.application.dtos.profile import (
    AthleteProfileOutput,
    CreateAthleteProfileInput,
    HeartRateZoneOutput,
    UpdateHeartRateDataInput,
    ViewHeartRateZonesInput,
)
from smart_pace.application.ports.unit_of_work import UnitOfWork
from smart_pace.application.use_cases._helpers import (
    build_athlete_profile_output,
    build_heart_rate_zones_output,
    ensure_profile_ownership,
)
from smart_pace.domain.entities.athlete_profile import AthleteProfile
from smart_pace.domain.exceptions import (
    ConflictException,
    EntityNotFoundException,
)
from smart_pace.domain.value_objects.heart_rate import HeartRate
from smart_pace.domain.value_objects.vo2max import Vo2max


class ProfileUseCases:
    def __init__(self, unit_of_work: Callable[[], UnitOfWork]) -> None:
        self.unit_of_work = unit_of_work

    async def create_profile(
        self, input_data: CreateAthleteProfileInput
    ) -> AthleteProfileOutput:
        """UC5 — Criar perfil de atleta."""
        async with self.unit_of_work() as uow:
            user = await uow.users.find_by_id(input_data.user_id)
            if user is None:
                raise EntityNotFoundException("User not found")

            existing_profile = await uow.athlete_profiles.find_by_user_id(
                input_data.user_id
            )
            if existing_profile is not None:
                raise ConflictException("Athlete profile already exists")

            resting_heart_rate = HeartRate(input_data.resting_heart_rate)
            maximum_heart_rate = HeartRate(input_data.maximum_heart_rate)
            current_vo2max = (
                Vo2max(input_data.current_vo2max)
                if input_data.current_vo2max is not None
                else None
            )

            profile = AthleteProfile(
                user_id=input_data.user_id,
                sport_type=input_data.sport_type,
                date_of_birth=input_data.date_of_birth,
                resting_heart_rate=resting_heart_rate,
                maximum_heart_rate=maximum_heart_rate,
                functional_threshold_power=input_data.functional_threshold_power,
                current_vo2max=current_vo2max,
                training_experience_years=input_data.training_experience_years,
                weekly_target_hours=input_data.weekly_target_hours,
            )
            await uow.athlete_profiles.save(profile)
            await uow.commit()

        zones = build_heart_rate_zones_output(profile)
        return build_athlete_profile_output(profile, zones)

    async def update_heart_rate(
        self, input_data: UpdateHeartRateDataInput
    ) -> AthleteProfileOutput:
        """UC6 — Atualizar dados de FC (inclui recálculo de zonas)."""
        async with self.unit_of_work() as uow:
            profile = await uow.athlete_profiles.find_by_id(
                input_data.athlete_profile_id
            )
            if profile is None:
                raise EntityNotFoundException("Athlete profile not found")

            ensure_profile_ownership(profile, input_data.user_id)

            resting_heart_rate = HeartRate(input_data.resting_heart_rate)
            maximum_heart_rate = HeartRate(input_data.maximum_heart_rate)
            profile.update_heart_rate(resting_heart_rate, maximum_heart_rate)

            await uow.athlete_profiles.save(profile)
            await uow.commit()

        zones = build_heart_rate_zones_output(profile)
        return build_athlete_profile_output(profile, zones)

    async def view_heart_rate_zones(
        self, input_data: ViewHeartRateZonesInput
    ) -> list[HeartRateZoneOutput]:
        """UC7 — Ver zonas de FC."""
        async with self.unit_of_work() as uow:
            profile = await uow.athlete_profiles.find_by_id(
                input_data.athlete_profile_id
            )
            if profile is None:
                raise EntityNotFoundException("Athlete profile not found")

            ensure_profile_ownership(profile, input_data.user_id)

        return build_heart_rate_zones_output(profile)
