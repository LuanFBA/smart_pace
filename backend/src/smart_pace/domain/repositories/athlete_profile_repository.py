from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from smart_pace.domain.entities.athlete_profile import AthleteProfile


class AthleteProfileRepository(ABC):
    @abstractmethod
    async def find_by_id(self, profile_id: UUID) -> AthleteProfile | None: ...

    @abstractmethod
    async def find_by_user_id(self, user_id: UUID) -> AthleteProfile | None: ...

    @abstractmethod
    async def save(self, profile: AthleteProfile) -> AthleteProfile: ...
