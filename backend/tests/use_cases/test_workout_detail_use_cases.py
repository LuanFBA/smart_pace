from __future__ import annotations

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from smart_pace.application.dtos.workout import (
    DeleteWorkoutLogInput,
    GetWorkoutLogInput,
    UpdateWorkoutLogInput,
)
from smart_pace.application.use_cases.workout_use_cases import WorkoutUseCases
from smart_pace.domain.exceptions import EntityNotFoundException, UnauthorizedException

from .conftest import LOG_ID, PROFILE_ID, SESSION_ID, USER_ID


@pytest.fixture
def use_cases(mock_uow, mock_clock):
    return WorkoutUseCases(unit_of_work=lambda: mock_uow, clock=mock_clock)


# --- get_workout_log ---

async def test_get_workout_log_returns_output(use_cases, sample_log):
    input_data = GetWorkoutLogInput(log_id=LOG_ID, user_id=USER_ID)
    result = await use_cases.get_workout_log(input_data)
    assert result.id == LOG_ID
    assert result.actual_distance_meters == 10000


async def test_get_workout_log_not_found_raises(use_cases, mock_uow):
    mock_uow.workout_logs.find_by_id = AsyncMock(return_value=None)
    with pytest.raises(EntityNotFoundException):
        await use_cases.get_workout_log(GetWorkoutLogInput(log_id=LOG_ID, user_id=USER_ID))


async def test_get_workout_log_wrong_user_raises(use_cases, mock_uow, sample_profile):
    other_user = uuid4()
    sample_profile.user_id = other_user  # perfil pertence a outro usuário
    with pytest.raises(UnauthorizedException):
        await use_cases.get_workout_log(GetWorkoutLogInput(log_id=LOG_ID, user_id=USER_ID))
