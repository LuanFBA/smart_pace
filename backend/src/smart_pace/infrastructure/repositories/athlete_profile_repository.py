from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from smart_pace.domain.entities.athlete_profile import AthleteProfile
from smart_pace.domain.repositories.athlete_profile_repository import (
    AthleteProfileRepository as AthleteProfileRepositoryPort,
)
from smart_pace.infrastructure.database.mappers import (
    athlete_profile_entity_to_model,
    athlete_profile_model_to_entity,
)
from smart_pace.infrastructure.database.models import AthleteProfileModel


class SqlAlchemyAthleteProfileRepository(AthleteProfileRepositoryPort):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, profile_id: UUID) -> AthleteProfile | None:
        result = await self._session.get(AthleteProfileModel, profile_id)
        return athlete_profile_model_to_entity(result) if result else None

    async def find_by_user_id(self, user_id: UUID) -> AthleteProfile | None:
        stmt = select(AthleteProfileModel).where(
            AthleteProfileModel.user_id == user_id
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return athlete_profile_model_to_entity(model) if model else None

    async def save(self, profile: AthleteProfile) -> AthleteProfile:
        model = athlete_profile_entity_to_model(profile)
        merged = await self._session.merge(model)
        await self._session.flush()
        return athlete_profile_model_to_entity(merged)
