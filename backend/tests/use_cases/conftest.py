from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from smart_pace.application.ports.clock import Clock
from smart_pace.application.ports.unit_of_work import UnitOfWork
from smart_pace.domain.entities.athlete_profile import AthleteProfile
from smart_pace.domain.entities.workout_log import WorkoutLog
from smart_pace.domain.entities.workout_session import WorkoutSession
from smart_pace.domain.enums import SessionStatus, SessionType, SportType
from smart_pace.domain.value_objects.distance import Distance
from smart_pace.domain.value_objects.duration import Duration
from smart_pace.domain.value_objects.heart_rate import HeartRate
from smart_pace.domain.value_objects.pace import Pace


USER_ID = uuid4()
PROFILE_ID = uuid4()
SESSION_ID = uuid4()
LOG_ID = uuid4()
NOW = datetime(2026, 4, 16, 10, 0, 0, tzinfo=UTC)


@pytest.fixture
def mock_clock() -> Clock:
    clock = MagicMock(spec=Clock)
    clock.now.return_value = NOW
    return clock


@pytest.fixture
def sample_profile() -> AthleteProfile:
    from datetime import date
    return AthleteProfile(
        id=PROFILE_ID,
        user_id=USER_ID,
        sport_type=SportType.RUNNING,
        date_of_birth=date(1990, 1, 1),
        resting_heart_rate=HeartRate(55),
        maximum_heart_rate=HeartRate(190),
    )


@pytest.fixture
def sample_session() -> WorkoutSession:
    from datetime import date
    return WorkoutSession(
        id=SESSION_ID,
        athlete_profile_id=PROFILE_ID,
        scheduled_date=date(2026, 4, 16),
        session_type=SessionType.EASY_RUN,
        status=SessionStatus.COMPLETED,
    )


@pytest.fixture
def sample_log() -> WorkoutLog:
    return WorkoutLog(
        id=LOG_ID,
        workout_session_id=SESSION_ID,
        athlete_profile_id=PROFILE_ID,
        started_at=datetime(2026, 4, 16, 8, 0, 0, tzinfo=UTC),
        finished_at=datetime(2026, 4, 16, 9, 0, 0, tzinfo=UTC),
        actual_distance=Distance(10000),
        actual_duration=Duration(3600),
        average_pace=Pace(360),
    )


@pytest.fixture
def mock_uow(sample_profile, sample_session, sample_log) -> UnitOfWork:
    uow = AsyncMock(spec=UnitOfWork)
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=False)

    uow.athlete_profiles = AsyncMock()
    uow.athlete_profiles.find_by_id = AsyncMock(return_value=sample_profile)

    uow.workout_sessions = AsyncMock()
    uow.workout_sessions.find_by_id = AsyncMock(return_value=sample_session)
    uow.workout_sessions.save = AsyncMock()

    uow.workout_logs = AsyncMock()
    uow.workout_logs.find_by_id = AsyncMock(return_value=sample_log)
    uow.workout_logs.save = AsyncMock(return_value=sample_log)
    uow.workout_logs.delete = AsyncMock()
    uow.workout_logs.find_since_date = AsyncMock(return_value=[])

    uow.performance_metrics = AsyncMock()
    uow.performance_metrics.find_latest_by_athlete_profile_id = AsyncMock(return_value=None)
    uow.performance_metrics.save = AsyncMock()

    uow.commit = AsyncMock()
    return uow
