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


from datetime import UTC, datetime


def _update_input(**overrides):
    defaults = dict(
        log_id=LOG_ID,
        user_id=USER_ID,
        started_at=datetime(2026, 4, 16, 8, 0, 0, tzinfo=UTC),
        finished_at=datetime(2026, 4, 16, 9, 30, 0, tzinfo=UTC),
        actual_distance_meters=12000,
        actual_duration_seconds=5400,
    )
    defaults.update(overrides)
    return UpdateWorkoutLogInput(**defaults)


async def test_update_workout_log_recalculates_pace(use_cases, mock_uow, sample_log):
    saved_logs = []

    async def capture_save(log):
        saved_logs.append(log)
        return log

    mock_uow.workout_logs.save = capture_save
    await use_cases.update_workout_log(_update_input())
    saved = saved_logs[0]
    # 12000m / 5400s → pace = 5400/12 = 450 sec/km
    assert saved.average_pace.seconds_per_kilometer == 450


async def test_update_workout_log_not_found_raises(use_cases, mock_uow):
    mock_uow.workout_logs.find_by_id = AsyncMock(return_value=None)
    with pytest.raises(EntityNotFoundException):
        await use_cases.update_workout_log(_update_input())


async def test_update_workout_log_preserves_id(use_cases, mock_uow, sample_log):
    saved_logs = []

    async def capture_save(log):
        saved_logs.append(log)
        return log

    mock_uow.workout_logs.save = capture_save
    await use_cases.update_workout_log(_update_input())
    assert saved_logs[0].id == LOG_ID
