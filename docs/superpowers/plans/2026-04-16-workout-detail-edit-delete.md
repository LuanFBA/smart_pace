# Workout Detail — Edit & Delete Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Adicionar tela de detalhe de treino com edição inline (toggle view/edit) e deleção com modal de confirmação, mais 3 novos endpoints de backend (GET, PUT, DELETE por log_id).

**Architecture:** O backend expõe 3 novos endpoints REST em `/workouts/logs/{log_id}` com ownership check via JWT. No frontend, `WorkoutCard` torna-se pressionável e navega para `(app)/workout/[id].tsx`, tela de stack que busca o log por ID, permite editar todos os campos com toggle view/edit e deletar com confirmação em modal customizado.

**Tech Stack:** Python 3.12 + FastAPI + SQLAlchemy 2 async (backend); React Native + Expo Router v6 + TypeScript (frontend); pytest + pytest-asyncio para testes de use cases.

---

## Mapa de arquivos

**Backend — criar:**
- `backend/tests/__init__.py`
- `backend/tests/use_cases/__init__.py`
- `backend/tests/use_cases/conftest.py` — fixtures de mocks compartilhados
- `backend/tests/use_cases/test_workout_detail_use_cases.py` — testes dos 3 novos use cases

**Backend — modificar:**
- `backend/src/smart_pace/domain/entities/workout_session.py` — adicionar `revert_to_scheduled()`
- `backend/src/smart_pace/domain/repositories/workout_log_repository.py` — método abstrato `delete`
- `backend/src/smart_pace/infrastructure/repositories/workout_log_repository.py` — implementação `delete`
- `backend/src/smart_pace/application/dtos/workout.py` — 3 novos DTOs de input
- `backend/src/smart_pace/application/use_cases/workout_use_cases.py` — 3 novos use cases
- `backend/src/smart_pace/interface/api/schemas/schemas.py` — `UpdateWorkoutLogRequest`
- `backend/src/smart_pace/interface/api/workouts.py` — 3 novas rotas

**Frontend — criar:**
- `mobile/app/(app)/workout/[id].tsx` — tela de detalhe

**Frontend — modificar:**
- `mobile/src/services/workout-service.ts` — adicionar `getWorkoutLog`, `updateWorkout`, `deleteWorkout`
- `mobile/src/components/WorkoutCard.tsx` — adicionar prop `onPress`, envolver em `Pressable`
- `mobile/app/(app)/(tabs)/activity-history.tsx` — adicionar `useFocusEffect`

---

## Task 1: Domain — revert_to_scheduled + repository delete

**Files:**
- Modify: `backend/src/smart_pace/domain/entities/workout_session.py`
- Modify: `backend/src/smart_pace/domain/repositories/workout_log_repository.py`
- Modify: `backend/src/smart_pace/infrastructure/repositories/workout_log_repository.py`

- [ ] **Adicionar `revert_to_scheduled()` em `WorkoutSession`**

Em `backend/src/smart_pace/domain/entities/workout_session.py`, após `mark_skipped`:

```python
def revert_to_scheduled(self) -> None:
    self.status = SessionStatus.SCHEDULED
```

- [ ] **Adicionar método abstrato `delete` em `WorkoutLogRepository`**

Em `backend/src/smart_pace/domain/repositories/workout_log_repository.py`:

```python
@abstractmethod
async def delete(self, log_id: UUID) -> None: ...
```

- [ ] **Implementar `delete` em `SqlAlchemyWorkoutLogRepository`**

Em `backend/src/smart_pace/infrastructure/repositories/workout_log_repository.py`, adicionar após `save`:

```python
async def delete(self, log_id: UUID) -> None:
    model = await self._session.get(WorkoutLogModel, log_id)
    if model:
        await self._session.delete(model)
        await self._session.flush()
```

- [ ] **Commit**

```bash
git add backend/src/smart_pace/domain/entities/workout_session.py \
        backend/src/smart_pace/domain/repositories/workout_log_repository.py \
        backend/src/smart_pace/infrastructure/repositories/workout_log_repository.py
git commit -m "feat(domain): add revert_to_scheduled and WorkoutLog.delete"
```

---

## Task 2: Backend DTOs + schema

**Files:**
- Modify: `backend/src/smart_pace/application/dtos/workout.py`
- Modify: `backend/src/smart_pace/interface/api/schemas/schemas.py`

- [ ] **Adicionar 3 novos DTOs em `dtos/workout.py`**

Adicionar após `GetNextWorkoutSuggestionInput`:

```python
class GetWorkoutLogInput(BaseModel):
    model_config = ConfigDict(frozen=True)

    log_id: UUID
    user_id: UUID


class UpdateWorkoutLogInput(BaseModel):
    model_config = ConfigDict(frozen=True)

    log_id: UUID
    user_id: UUID
    started_at: datetime
    finished_at: datetime
    actual_distance_meters: int
    actual_duration_seconds: int
    average_heart_rate: int | None = None
    maximum_heart_rate: int | None = None
    perceived_exertion: int | None = None
    notes: str | None = None
    average_power_watts: int | None = None


class DeleteWorkoutLogInput(BaseModel):
    model_config = ConfigDict(frozen=True)

    log_id: UUID
    user_id: UUID
```

- [ ] **Adicionar `UpdateWorkoutLogRequest` em `schemas.py`**

Adicionar ao final de `schemas.py`:

```python
class UpdateWorkoutLogRequest(BaseModel):
    started_at: datetime
    finished_at: datetime
    actual_distance_meters: int
    actual_duration_seconds: int
    average_heart_rate: int | None = None
    maximum_heart_rate: int | None = None
    perceived_exertion: int | None = None
    notes: str | None = None
    average_power_watts: int | None = None
```

- [ ] **Commit**

```bash
git add backend/src/smart_pace/application/dtos/workout.py \
        backend/src/smart_pace/interface/api/schemas/schemas.py
git commit -m "feat(dtos): add GetWorkoutLogInput, UpdateWorkoutLogInput, DeleteWorkoutLogInput"
```

---

## Task 3: Infraestrutura de testes

**Files:**
- Create: `backend/tests/__init__.py`
- Create: `backend/tests/use_cases/__init__.py`
- Create: `backend/tests/use_cases/conftest.py`

- [ ] **Criar arquivos `__init__.py`**

```bash
mkdir -p backend/tests/use_cases
touch backend/tests/__init__.py backend/tests/use_cases/__init__.py
```

- [ ] **Criar `conftest.py` com fixtures**

Criar `backend/tests/use_cases/conftest.py`:

```python
from __future__ import annotations

import asyncio
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
    from smart_pace.domain.value_objects.heart_rate import HeartRate
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
```

- [ ] **Verificar que pytest descobre os arquivos**

```bash
cd backend && uv run pytest tests/ --collect-only 2>&1 | head -20
```

Expected: lista vazia de testes (nenhum erro de importação).

- [ ] **Commit**

```bash
git add backend/tests/
git commit -m "test: setup pytest infrastructure with shared fixtures"
```

---

## Task 4: Use case `get_workout_log` (TDD)

**Files:**
- Create: `backend/tests/use_cases/test_workout_detail_use_cases.py`
- Modify: `backend/src/smart_pace/application/use_cases/workout_use_cases.py`

- [ ] **Escrever testes para `get_workout_log`**

Criar `backend/tests/use_cases/test_workout_detail_use_cases.py`:

```python
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
```

- [ ] **Executar e confirmar FAIL**

```bash
cd backend && uv run pytest tests/use_cases/test_workout_detail_use_cases.py -v 2>&1 | tail -20
```

Expected: `AttributeError: 'WorkoutUseCases' object has no attribute 'get_workout_log'`

- [ ] **Implementar `get_workout_log` em `workout_use_cases.py`**

Adicionar às importações de dtos:
```python
from smart_pace.application.dtos.workout import (
    ...
    DeleteWorkoutLogInput,
    GetWorkoutLogInput,
    UpdateWorkoutLogInput,
)
```

Adicionar método em `WorkoutUseCases` após `get_next_suggestion`:

```python
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
```

- [ ] **Executar e confirmar PASS**

```bash
cd backend && uv run pytest tests/use_cases/test_workout_detail_use_cases.py::test_get_workout_log_returns_output tests/use_cases/test_workout_detail_use_cases.py::test_get_workout_log_not_found_raises tests/use_cases/test_workout_detail_use_cases.py::test_get_workout_log_wrong_user_raises -v
```

Expected: 3 passed.

- [ ] **Commit**

```bash
git add tests/use_cases/test_workout_detail_use_cases.py \
        backend/src/smart_pace/application/use_cases/workout_use_cases.py \
        backend/src/smart_pace/application/dtos/workout.py
git commit -m "feat(use-case): add get_workout_log with TDD"
```

---

## Task 5: Use case `update_workout_log` (TDD)

**Files:**
- Modify: `backend/tests/use_cases/test_workout_detail_use_cases.py`
- Modify: `backend/src/smart_pace/application/use_cases/workout_use_cases.py`

- [ ] **Adicionar testes para `update_workout_log`**

Adicionar ao final de `test_workout_detail_use_cases.py`:

```python
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
    from smart_pace.domain.entities.workout_log import WorkoutLog

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
```

- [ ] **Executar e confirmar FAIL**

```bash
cd backend && uv run pytest tests/use_cases/test_workout_detail_use_cases.py -k "update" -v 2>&1 | tail -10
```

Expected: `AttributeError: 'WorkoutUseCases' object has no attribute 'update_workout_log'`

- [ ] **Implementar `update_workout_log`**

Adicionar em `WorkoutUseCases` após `get_workout_log`:

```python
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
        object.__setattr__(updated_log, "id", existing.id)

        await uow.workout_logs.save(updated_log)
        await self._recalculate_performance_metrics(uow, profile)
        await uow.commit()

        session = await uow.workout_sessions.find_by_id(existing.workout_session_id)
        session_type = session.session_type.value if session else "easy_run"

    return _build_workout_log_output(updated_log, session_type)
```

> **Nota:** `WorkoutLog` não é frozen, então a atribuição direta `updated_log.id = existing.id` também funciona. Use `object.__setattr__` apenas se encontrar erro de frozen dataclass.

- [ ] **Executar e confirmar PASS**

```bash
cd backend && uv run pytest tests/use_cases/test_workout_detail_use_cases.py -k "update" -v
```

Expected: 3 passed.

- [ ] **Commit**

```bash
git add tests/use_cases/test_workout_detail_use_cases.py \
        backend/src/smart_pace/application/use_cases/workout_use_cases.py
git commit -m "feat(use-case): add update_workout_log with TDD"
```

---

## Task 6: Use case `delete_workout_log` (TDD)

**Files:**
- Modify: `backend/tests/use_cases/test_workout_detail_use_cases.py`
- Modify: `backend/src/smart_pace/application/use_cases/workout_use_cases.py`

- [ ] **Adicionar testes para `delete_workout_log`**

Adicionar ao final de `test_workout_detail_use_cases.py`:

```python
from smart_pace.domain.enums import SessionStatus


async def test_delete_workout_log_reverts_session(use_cases, mock_uow, sample_session):
    saved_sessions = []

    async def capture_session_save(s):
        saved_sessions.append(s)

    mock_uow.workout_sessions.save = capture_session_save
    await use_cases.delete_workout_log(DeleteWorkoutLogInput(log_id=LOG_ID, user_id=USER_ID))
    assert saved_sessions[0].status == SessionStatus.SCHEDULED


async def test_delete_workout_log_calls_delete(use_cases, mock_uow):
    deleted_ids = []

    async def capture_delete(lid):
        deleted_ids.append(lid)

    mock_uow.workout_logs.delete = capture_delete
    await use_cases.delete_workout_log(DeleteWorkoutLogInput(log_id=LOG_ID, user_id=USER_ID))
    assert LOG_ID in deleted_ids


async def test_delete_workout_log_not_found_raises(use_cases, mock_uow):
    mock_uow.workout_logs.find_by_id = AsyncMock(return_value=None)
    with pytest.raises(EntityNotFoundException):
        await use_cases.delete_workout_log(DeleteWorkoutLogInput(log_id=LOG_ID, user_id=USER_ID))
```

- [ ] **Executar e confirmar FAIL**

```bash
cd backend && uv run pytest tests/use_cases/test_workout_detail_use_cases.py -k "delete" -v 2>&1 | tail -10
```

Expected: `AttributeError: 'WorkoutUseCases' object has no attribute 'delete_workout_log'`

- [ ] **Implementar `delete_workout_log`**

Adicionar em `WorkoutUseCases` após `update_workout_log`:

```python
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
```

- [ ] **Executar todos os testes**

```bash
cd backend && uv run pytest tests/use_cases/test_workout_detail_use_cases.py -v
```

Expected: 9 passed, 0 failed.

- [ ] **Commit**

```bash
git add tests/use_cases/test_workout_detail_use_cases.py \
        backend/src/smart_pace/application/use_cases/workout_use_cases.py
git commit -m "feat(use-case): add delete_workout_log with TDD"
```

---

## Task 7: API routes (GET, PUT, DELETE)

**Files:**
- Modify: `backend/src/smart_pace/interface/api/workouts.py`

- [ ] **Adicionar imports necessários em `workouts.py`**

Adicionar aos imports existentes:

```python
from smart_pace.application.dtos.workout import (
    DeleteWorkoutLogInput,
    GetWorkoutLogInput,
    UpdateWorkoutLogInput,
    ...  # manter os existentes
)
from smart_pace.interface.api.schemas.schemas import (
    LogWorkoutRequest,
    ScheduleWorkoutSessionRequest,
    UpdateWorkoutLogRequest,
)
```

- [ ] **Adicionar as 3 novas rotas**

Adicionar ao final de `workouts.py`:

```python
@router.get("/logs/{log_id}", response_model=WorkoutLogOutput)
async def get_workout_log(
    log_id: UUID,
    current_user: TokenPayload = Depends(get_current_user),
    container: Container = Depends(get_container),
) -> WorkoutLogOutput:
    """Buscar log de treino por ID."""
    return await container.workout_use_cases().get_workout_log(
        GetWorkoutLogInput(log_id=log_id, user_id=current_user.user_id)
    )


@router.put("/logs/{log_id}", response_model=WorkoutLogOutput)
async def update_workout_log(
    log_id: UUID,
    body: UpdateWorkoutLogRequest,
    current_user: TokenPayload = Depends(get_current_user),
    container: Container = Depends(get_container),
) -> WorkoutLogOutput:
    """Substituir todos os campos editáveis de um log de treino."""
    return await container.workout_use_cases().update_workout_log(
        UpdateWorkoutLogInput(
            log_id=log_id,
            user_id=current_user.user_id,
            started_at=body.started_at,
            finished_at=body.finished_at,
            actual_distance_meters=body.actual_distance_meters,
            actual_duration_seconds=body.actual_duration_seconds,
            average_heart_rate=body.average_heart_rate,
            maximum_heart_rate=body.maximum_heart_rate,
            perceived_exertion=body.perceived_exertion,
            notes=body.notes,
            average_power_watts=body.average_power_watts,
        )
    )


@router.delete("/logs/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workout_log(
    log_id: UUID,
    current_user: TokenPayload = Depends(get_current_user),
    container: Container = Depends(get_container),
) -> None:
    """Remover log de treino e reverter sessão para scheduled."""
    await container.workout_use_cases().delete_workout_log(
        DeleteWorkoutLogInput(log_id=log_id, user_id=current_user.user_id)
    )
```

- [ ] **Verificar que o servidor inicia sem erros**

```bash
cd backend && uv run python -c "from smart_pace.interface.api.workouts import router; print('OK')"
```

Expected: `OK`

- [ ] **Commit**

```bash
git add backend/src/smart_pace/interface/api/workouts.py \
        backend/src/smart_pace/interface/api/schemas/schemas.py
git commit -m "feat(api): add GET/PUT/DELETE /workouts/logs/{log_id}"
```

---

## Task 8: Frontend — service functions

**Files:**
- Modify: `mobile/src/services/workout-service.ts`

- [ ] **Adicionar os 3 novos payloads e funções**

Adicionar após `LogWorkoutPayload` em `workout-service.ts`:

```typescript
export interface UpdateWorkoutPayload {
  started_at: string;
  finished_at: string;
  actual_distance_meters: number;
  actual_duration_seconds: number;
  average_heart_rate?: number | null;
  maximum_heart_rate?: number | null;
  perceived_exertion?: number | null;
  notes?: string | null;
  average_power_watts?: number | null;
}
```

Adicionar após `logWorkout`:

```typescript
export async function getWorkoutLog(logId: string): Promise<WorkoutLog> {
  return apiRequest<WorkoutLog>(`/workouts/logs/${logId}`, {
    authenticated: true,
  });
}

export async function updateWorkout(
  logId: string,
  data: UpdateWorkoutPayload,
): Promise<WorkoutLog> {
  return apiRequest<WorkoutLog>(`/workouts/logs/${logId}`, {
    method: "PUT",
    authenticated: true,
    body: JSON.stringify(data),
  });
}

export async function deleteWorkout(logId: string): Promise<void> {
  await apiRequest<void>(`/workouts/logs/${logId}`, {
    method: "DELETE",
    authenticated: true,
  });
}
```

- [ ] **Verificar tipos**

```bash
cd mobile && npx tsc --noEmit 2>&1 | grep -c "error" || echo "0 errors"
```

Expected: `0 errors`

- [ ] **Commit**

```bash
git add mobile/src/services/workout-service.ts
git commit -m "feat(service): add getWorkoutLog, updateWorkout, deleteWorkout"
```

---

## Task 9: Frontend — WorkoutCard pressable + activity-history useFocusEffect

**Files:**
- Modify: `mobile/src/components/WorkoutCard.tsx`
- Modify: `mobile/app/(app)/(tabs)/activity-history.tsx`

- [ ] **Tornar WorkoutCard pressionável**

Em `mobile/src/components/WorkoutCard.tsx`, adicionar prop `onPress` e envolver o card:

```typescript
// Adicionar Pressable ao import de react-native
import { Pressable, StyleSheet, Text, View, type TextStyle } from "react-native";

interface WorkoutCardProps {
  log: WorkoutLog;
  onPress?: () => void;  // ← adicionar
}

export function WorkoutCard({ log, onPress }: WorkoutCardProps) {
  // ...
  return (
    <Pressable onPress={onPress} disabled={!onPress}>
      <Card variant="flat" padding="base" style={styles.card}>
        {/* conteúdo existente sem alterações */}
      </Card>
    </Pressable>
  );
}
```

- [ ] **Passar `onPress` em `activity-history.tsx`**

Em `activity-history.tsx`, adicionar import de `router` e `useFocusEffect`:

```typescript
import { useCallback, useEffect, useState } from "react";
import { useFocusEffect } from "expo-router";
import { router } from "expo-router";
```

Substituir o `useEffect` de carga inicial por `useFocusEffect`:

```typescript
// Substituir:
useEffect(() => {
  setIsLoading(true);
  setError(null);
  fetchPage(0, true).finally(() => setIsLoading(false));
}, [fetchPage]);

// Por:
useFocusEffect(
  useCallback(() => {
    setIsLoading(true);
    setError(null);
    fetchPage(0, true).finally(() => setIsLoading(false));
  }, [fetchPage]),
);
```

Atualizar `renderItem` na `FlatList`:

```typescript
renderItem={({ item }) => (
  <WorkoutCard
    log={item}
    onPress={() => router.push(`/(app)/workout/${item.id}`)}
  />
)}
```

- [ ] **Verificar tipos**

```bash
cd mobile && npx tsc --noEmit 2>&1 | grep -c "error" || echo "0 errors"
```

Expected: `0 errors`

- [ ] **Commit**

```bash
git add mobile/src/components/WorkoutCard.tsx \
        mobile/app/(app)/(tabs)/activity-history.tsx
git commit -m "feat(ui): WorkoutCard pressable, activity-history useFocusEffect"
```

---

## Task 10: Frontend — tela de detalhe (view mode)

**Files:**
- Create: `mobile/app/(app)/workout/[id].tsx`

- [ ] **Criar diretório e arquivo base com view mode**

Criar `mobile/app/(app)/workout/[id].tsx`:

```typescript
import { useCallback, useState } from "react";
import {
  ActivityIndicator,
  Modal,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  View,
  type TextStyle,
  type ViewStyle,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { router, useLocalSearchParams, useFocusEffect } from "expo-router";
import { Pencil, Trash2 } from "lucide-react-native";

import { Button } from "../../../src/components/Button";
import { Card } from "../../../src/components/Card";
import { Skeleton } from "../../../src/components/Skeleton";
import { getWorkoutLog, deleteWorkout } from "../../../src/services/workout-service";
import { ApiError } from "../../../src/types/api";
import type { WorkoutLog } from "../../../src/types/api";
import { colors, radii, shadows, spacing, typography } from "../../../src/theme";
import {
  formatDate,
  formatDurationCompact,
  formatPace,
  formatRelativeDate,
  formatSpeed,
  metersToKm,
} from "../../../src/utils/format";
import { SESSION_TYPE_LABELS } from "../../../src/utils/session-labels";
import { sessionTypeToSport } from "../../../src/utils/workout-stats";

export default function WorkoutDetailScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();

  const [log, setLog] = useState<WorkoutLog | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [isEditMode, setIsEditMode] = useState(false);

  const fetchLog = useCallback(async () => {
    if (!id) return;
    setIsLoading(true);
    setError(null);
    try {
      const data = await getWorkoutLog(id);
      setLog(data);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Erro ao carregar treino");
    } finally {
      setIsLoading(false);
    }
  }, [id]);

  useFocusEffect(useCallback(() => { fetchLog(); }, [fetchLog]));

  async function handleDelete() {
    if (!id) return;
    setIsDeleting(true);
    try {
      await deleteWorkout(id);
      router.back();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Erro ao excluir treino");
      setShowDeleteModal(false);
    } finally {
      setIsDeleting(false);
    }
  }

  if (isLoading) {
    return (
      <SafeAreaView style={styles.root} edges={["top"]}>
        <View style={styles.header}>
          <Skeleton width={120} height={16} />
          <Skeleton width={36} height={36} borderRadius={radii.md} />
        </View>
        <View style={styles.content}>
          <Skeleton height={100} />
          <Skeleton height={160} />
        </View>
      </SafeAreaView>
    );
  }

  if (error || !log) {
    return (
      <SafeAreaView style={styles.centered}>
        <Text style={styles.errorText}>{error ?? "Treino não encontrado"}</Text>
        <Button label="Tentar novamente" variant="ghost" onPress={fetchLog} />
      </SafeAreaView>
    );
  }

  if (isEditMode) {
    return (
      <EditMode
        log={log}
        onCancel={() => setIsEditMode(false)}
        onSaved={(updated) => { setLog(updated); setIsEditMode(false); }}
      />
    );
  }

  const isCycling = sessionTypeToSport(log.session_type) === "cycling";
  const typeLabel = SESSION_TYPE_LABELS[log.session_type] ?? log.session_type;

  return (
    <SafeAreaView style={styles.root} edges={["top"]}>
      {/* Cabeçalho */}
      <View style={styles.header}>
        <Text style={styles.headerDate}>{formatRelativeDate(log.started_at)}</Text>
        <Pressable onPress={() => setIsEditMode(true)} hitSlop={8} style={styles.editButton}>
          <Pencil color={colors.accent} size={18} strokeWidth={2} />
        </Pressable>
      </View>

      <ScrollView
        style={styles.scroll}
        contentContainerStyle={styles.content}
        showsVerticalScrollIndicator={false}
      >
        {/* Badge de tipo */}
        <View style={styles.typeBadgeRow}>
          <View style={[styles.typeBadge, isCycling && styles.typeBadgeCycling]}>
            <Text style={[styles.typeBadgeText, isCycling && styles.typeBadgeTextCycling]}>
              {typeLabel}
            </Text>
          </View>
          <Text style={styles.fullDate}>
            {formatDate(log.started_at)} {log.started_at.slice(11, 16)}
          </Text>
        </View>

        {/* Bloco primário de métricas */}
        <Card variant="flat" padding="base" style={styles.primaryBlock}>
          <View style={styles.primaryRow}>
            <MetricBlock label="Distância" value={metersToKm(log.actual_distance_meters)} unit="km" large />
            <View style={styles.blockDivider} />
            <MetricBlock label="Tempo" value={formatDurationCompact(log.actual_duration_seconds)} />
            <View style={styles.blockDivider} />
            {isCycling ? (
              <MetricBlock
                label="Velocidade"
                value={formatSpeed(log.actual_distance_meters, log.actual_duration_seconds)}
                unit="km/h"
              />
            ) : (
              <MetricBlock
                label="Pace"
                value={formatPace(log.average_pace_seconds_per_km)}
                unit="/km"
              />
            )}
          </View>
        </Card>

        {/* Métricas opcionais */}
        {(log.average_heart_rate != null ||
          log.maximum_heart_rate != null ||
          log.average_power_watts != null ||
          log.perceived_exertion != null ||
          log.notes) && (
          <Card variant="flat" padding="base" style={styles.metricsBlock}>
            {log.average_heart_rate != null && (
              <MetricRow label="FC média" value={`${log.average_heart_rate} bpm`} />
            )}
            {log.maximum_heart_rate != null && (
              <MetricRow label="FC máxima" value={`${log.maximum_heart_rate} bpm`} />
            )}
            {isCycling && log.average_power_watts != null && (
              <MetricRow label="Potência média" value={`${log.average_power_watts} W`} />
            )}
            {log.perceived_exertion != null && (
              <MetricRow label="Esforço (RPE)" value={`${log.perceived_exertion}/10`} />
            )}
            {log.notes ? (
              <View style={styles.notesRow}>
                <Text style={styles.notesLabel}>Notas</Text>
                <Text style={styles.notesValue}>{log.notes}</Text>
              </View>
            ) : null}
          </Card>
        )}

        {/* Botão excluir */}
        <Button
          label="Excluir treino"
          variant="danger"
          leftIcon={Trash2}
          fullWidth
          onPress={() => setShowDeleteModal(true)}
        />
      </ScrollView>

      {/* Modal de confirmação de deleção */}
      <Modal
        visible={showDeleteModal}
        transparent
        animationType="fade"
        onRequestClose={() => setShowDeleteModal(false)}
      >
        <Pressable style={styles.modalOverlay} onPress={() => setShowDeleteModal(false)} />
        <View style={styles.modalWrapper}>
          <Card variant="flat" padding="base" style={[styles.modalCard, shadows.lg as ViewStyle]}>
            <Text style={styles.modalTitle}>Excluir treino?</Text>
            <Text style={styles.modalBody}>
              Esta ação não pode ser desfeita. O treino será removido permanentemente.
            </Text>
            <View style={styles.modalActions}>
              <Button
                label="Cancelar"
                variant="ghost"
                onPress={() => setShowDeleteModal(false)}
                style={styles.modalBtn}
              />
              <Button
                label="Sim, excluir"
                variant="danger"
                loading={isDeleting}
                onPress={handleDelete}
                style={styles.modalBtn}
              />
            </View>
          </Card>
        </View>
      </Modal>
    </SafeAreaView>
  );
}
```

Adicionar componentes internos de view e styles (ainda sem EditMode):

```typescript
function MetricBlock({
  label,
  value,
  unit,
  large,
}: {
  label: string;
  value: string;
  unit?: string;
  large?: boolean;
}) {
  return (
    <View style={metricBlockStyles.container}>
      <Text style={metricBlockStyles.label}>{label}</Text>
      <View style={metricBlockStyles.valueRow}>
        <Text style={[metricBlockStyles.value, large && metricBlockStyles.valueLarge]}>
          {value}
        </Text>
        {unit ? <Text style={metricBlockStyles.unit}>{unit}</Text> : null}
      </View>
    </View>
  );
}

function MetricRow({ label, value }: { label: string; value: string }) {
  return (
    <View style={metricRowStyles.row}>
      <Text style={metricRowStyles.label}>{label}</Text>
      <Text style={metricRowStyles.value}>{value}</Text>
    </View>
  );
}

// Placeholder para Task 11
function EditMode({
  log,
  onCancel,
  onSaved,
}: {
  log: WorkoutLog;
  onCancel: () => void;
  onSaved: (updated: WorkoutLog) => void;
}) {
  return (
    <SafeAreaView style={styles.root} edges={["top"]}>
      <Text style={{ color: colors.textPrimary, padding: spacing.xl }}>
        Edit mode — em breve
      </Text>
      <Button label="Cancelar" variant="ghost" onPress={onCancel} />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: colors.background },
  centered: {
    flex: 1,
    backgroundColor: colors.background,
    alignItems: "center",
    justifyContent: "center",
    paddingHorizontal: spacing["2xl"],
    gap: spacing.sm,
  },
  header: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    paddingHorizontal: spacing.xl,
    paddingVertical: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  headerDate: {
    ...(typography.titleSm as TextStyle),
    color: colors.textPrimary,
  },
  editButton: {
    padding: spacing.xs,
  },
  scroll: { flex: 1 },
  content: {
    paddingHorizontal: spacing.xl,
    paddingTop: spacing.lg,
    paddingBottom: spacing["3xl"],
    gap: spacing.lg,
  },
  typeBadgeRow: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
  },
  typeBadge: {
    paddingHorizontal: spacing.sm,
    paddingVertical: 4,
    borderRadius: radii.pill,
    backgroundColor: colors.accentSoft,
  },
  typeBadgeCycling: { backgroundColor: colors.successSoft },
  typeBadgeText: {
    ...(typography.caption as TextStyle),
    color: colors.accent,
    fontWeight: "600",
  },
  typeBadgeTextCycling: { color: colors.success },
  fullDate: {
    ...(typography.caption as TextStyle),
    color: colors.textTertiary,
  },
  primaryBlock: { gap: spacing.sm },
  primaryRow: {
    flexDirection: "row",
    alignItems: "center",
  },
  blockDivider: {
    width: 1,
    height: 40,
    backgroundColor: colors.border,
    marginHorizontal: spacing.md,
  },
  metricsBlock: { gap: spacing.xs },
  notesRow: { gap: spacing.xs, marginTop: spacing.xs },
  notesLabel: {
    ...(typography.caption as TextStyle),
    color: colors.textTertiary,
  },
  notesValue: {
    ...(typography.body as TextStyle),
    color: colors.textPrimary,
    lineHeight: 22,
  },
  errorText: {
    ...(typography.bodySm as TextStyle),
    color: colors.danger,
    textAlign: "center",
  },
  // Modal
  modalOverlay: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: "rgba(0,0,0,0.45)",
  },
  modalWrapper: {
    position: "absolute",
    left: spacing.xl,
    right: spacing.xl,
    top: "35%",
  },
  modalCard: { gap: spacing.base },
  modalTitle: {
    ...(typography.titleSm as TextStyle),
    color: colors.textPrimary,
  },
  modalBody: {
    ...(typography.body as TextStyle),
    color: colors.textSecondary,
    lineHeight: 22,
  },
  modalActions: {
    flexDirection: "row",
    gap: spacing.sm,
    marginTop: spacing.xs,
  },
  modalBtn: { flex: 1 },
});

const metricBlockStyles = StyleSheet.create({
  container: { flex: 1, alignItems: "center", gap: 2 },
  label: {
    ...(typography.caption as TextStyle),
    color: colors.textTertiary,
  },
  valueRow: { flexDirection: "row", alignItems: "baseline", gap: 2 },
  value: {
    ...(typography.titleSm as TextStyle),
    color: colors.textPrimary,
    fontWeight: "700",
  },
  valueLarge: { fontSize: 26 },
  unit: {
    ...(typography.caption as TextStyle),
    color: colors.textSecondary,
  },
});

const metricRowStyles = StyleSheet.create({
  row: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingVertical: spacing.xs,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  label: {
    ...(typography.body as TextStyle),
    color: colors.textSecondary,
  },
  value: {
    ...(typography.bodyStrong as TextStyle),
    color: colors.textPrimary,
  },
});
```

- [ ] **Verificar tipos**

```bash
cd mobile && npx tsc --noEmit 2>&1 | grep "workout/\[id\]" | head -10
```

Expected: sem erros neste arquivo.

- [ ] **Commit**

```bash
git add mobile/app/(app)/workout/
git commit -m "feat(screen): add workout detail view mode with delete modal"
```

---

## Task 11: Frontend — edit mode completo

**Files:**
- Modify: `mobile/app/(app)/workout/[id].tsx`

- [ ] **Substituir o componente `EditMode` placeholder pela implementação completa**

Substituir a função `EditMode` placeholder pelo seguinte:

```typescript
import {
  KeyboardAvoidingView,
  Platform,
} from "react-native";
import DateTimePicker, { type DateTimePickerEvent } from "@react-native-community/datetimepicker";
import { updateWorkout } from "../../../src/services/workout-service";

function EditMode({
  log,
  onCancel,
  onSaved,
}: {
  log: WorkoutLog;
  onCancel: () => void;
  onSaved: (updated: WorkoutLog) => void;
}) {
  const isCycling = sessionTypeToSport(log.session_type) === "cycling";

  // Inicializa campos a partir do log existente
  const initDate = new Date(log.started_at);
  const initStartTime = `${pad(initDate.getHours())}:${pad(initDate.getMinutes())}`;
  const durationSecs = log.actual_duration_seconds;
  const durationHours = Math.floor(durationSecs / 3600);
  const durationMins = Math.floor((durationSecs % 3600) / 60);
  const initDuration = `${pad(durationHours)}:${pad(durationMins)}`;
  const initDistKm = (log.actual_distance_meters / 1000).toFixed(2);

  const [workoutDate, setWorkoutDate] = useState(initDate);
  const [showDatePicker, setShowDatePicker] = useState(false);
  const [tempDate, setTempDate] = useState(initDate);
  const [startTime, setStartTime] = useState(initStartTime);
  const [duration, setDuration] = useState(initDuration);
  const [distanceKm, setDistanceKm] = useState(initDistKm);
  const [avgHr, setAvgHr] = useState(log.average_heart_rate != null ? String(log.average_heart_rate) : "");
  const [maxHr, setMaxHr] = useState(log.maximum_heart_rate != null ? String(log.maximum_heart_rate) : "");
  const [power, setPower] = useState(log.average_power_watts != null ? String(log.average_power_watts) : "");
  const [rpe, setRpe] = useState<number | null>(log.perceived_exertion ?? null);
  const [notes, setNotes] = useState(log.notes ?? "");
  const [isSaving, setIsSaving] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});

  function validate(): boolean {
    const errors: Record<string, string> = {};
    if (!startTime || startTime.length < 5) errors.startTime = "Informe o horário (HH:MM)";
    if (!duration || timeToSeconds(duration) === null || timeToSeconds(duration)! <= 0)
      errors.duration = "Duração inválida (HH:MM)";
    const dist = parseFloat(distanceKm) * 1000;
    if (!distanceKm || isNaN(dist) || dist <= 0) errors.distanceKm = "Distância inválida";
    if (avgHr) {
      const v = parseInt(avgHr, 10);
      if (isNaN(v) || v < 30 || v > 250) errors.avgHr = "FC inválida (30–250)";
    }
    if (maxHr) {
      const v = parseInt(maxHr, 10);
      if (isNaN(v) || v < 30 || v > 250) errors.maxHr = "FC inválida (30–250)";
    }
    if (isCycling && power) {
      const v = parseInt(power, 10);
      if (isNaN(v) || v <= 0) errors.power = "Potência inválida (> 0 W)";
    }
    setFieldErrors(errors);
    return Object.keys(errors).length === 0;
  }

  async function handleSave() {
    if (!validate()) return;
    setIsSaving(true);
    setSaveError(null);
    try {
      const isoDate = dateToISO(workoutDate);
      const durationSecs = timeToSeconds(duration)!;
      const startedAt = buildDatetime(isoDate, startTime);
      const finishedAtDate = new Date(startedAt);
      finishedAtDate.setSeconds(finishedAtDate.getSeconds() + durationSecs);
      const finishedAt =
        `${finishedAtDate.getFullYear()}-${pad(finishedAtDate.getMonth() + 1)}-${pad(finishedAtDate.getDate())}` +
        `T${pad(finishedAtDate.getHours())}:${pad(finishedAtDate.getMinutes())}:${pad(finishedAtDate.getSeconds())}`;

      const updated = await updateWorkout(log.id, {
        started_at: startedAt,
        finished_at: finishedAt,
        actual_distance_meters: Math.round(parseFloat(distanceKm) * 1000),
        actual_duration_seconds: durationSecs,
        average_heart_rate: avgHr ? parseInt(avgHr, 10) : null,
        maximum_heart_rate: maxHr ? parseInt(maxHr, 10) : null,
        perceived_exertion: rpe,
        notes: notes.trim() || null,
        average_power_watts: isCycling && power ? parseInt(power, 10) : null,
      });
      onSaved(updated);
    } catch (err) {
      setSaveError(err instanceof ApiError ? err.message : "Erro ao salvar treino");
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <SafeAreaView style={styles.root} edges={["top"]}>
      <View style={styles.header}>
        <Text style={styles.headerDate}>Editar treino</Text>
      </View>
      <KeyboardAvoidingView
        style={{ flex: 1 }}
        behavior={Platform.OS === "ios" ? "padding" : undefined}
      >
        <ScrollView
          style={styles.scroll}
          contentContainerStyle={styles.content}
          keyboardShouldPersistTaps="handled"
          showsVerticalScrollIndicator={false}
        >
          <Card variant="flat" padding="base" style={editStyles.card}>
            {/* Data */}
            <EditField label="Data">
              <Pressable
                style={editStyles.dateField}
                onPress={() => { setTempDate(workoutDate); setShowDatePicker(true); }}
              >
                <Text style={editStyles.dateText}>{dateToDisplay(workoutDate)}</Text>
              </Pressable>
            </EditField>

            {Platform.OS === "android" && showDatePicker && (
              <DateTimePicker
                value={workoutDate}
                mode="date"
                display="calendar"
                maximumDate={new Date()}
                onChange={(_: DateTimePickerEvent, d?: Date) => {
                  setShowDatePicker(false);
                  if (d) setWorkoutDate(d);
                }}
              />
            )}

            {/* Início e Duração */}
            <View style={styles.row}>
              <View style={styles.rowField}>
                <EditFormField
                  label="Início"
                  placeholder="HH:MM"
                  value={startTime}
                  onChangeText={(t) => setStartTime(applyTimeMask(t))}
                  keyboardType="numeric"
                  error={fieldErrors.startTime}
                />
              </View>
              <View style={styles.rowField}>
                <EditFormField
                  label="Duração"
                  placeholder="HH:MM"
                  value={duration}
                  onChangeText={(t) => setDuration(applyTimeMask(t))}
                  keyboardType="numeric"
                  error={fieldErrors.duration}
                />
              </View>
            </View>

            {/* Distância */}
            <EditFormField
              label="Distância (km)"
              placeholder="ex: 10.5"
              value={distanceKm}
              onChangeText={setDistanceKm}
              keyboardType="decimal-pad"
              error={fieldErrors.distanceKm}
            />

            {/* FC */}
            <View style={styles.row}>
              <View style={styles.rowField}>
                <EditFormField
                  label="FC média (bpm)"
                  placeholder="ex: 148"
                  value={avgHr}
                  onChangeText={setAvgHr}
                  keyboardType="numeric"
                  error={fieldErrors.avgHr}
                />
              </View>
              <View style={styles.rowField}>
                <EditFormField
                  label="FC máxima (bpm)"
                  placeholder="ex: 172"
                  value={maxHr}
                  onChangeText={setMaxHr}
                  keyboardType="numeric"
                  error={fieldErrors.maxHr}
                />
              </View>
            </View>

            {/* Potência — só para ciclismo */}
            {isCycling && (
              <EditFormField
                label="Potência média (W)"
                placeholder="ex: 220"
                value={power}
                onChangeText={setPower}
                keyboardType="numeric"
                error={fieldErrors.power}
              />
            )}

            {/* RPE */}
            <View>
              <Text style={fieldStyles.label}>Esforço percebido (RPE)</Text>
              <View style={styles.rpeRow}>
                {Array.from({ length: 10 }, (_, i) => i + 1).map((n) => (
                  <Pressable
                    key={n}
                    style={[styles.rpeChip, rpe === n && styles.rpeChipSelected]}
                    onPress={() => setRpe(rpe === n ? null : n)}
                  >
                    <Text style={[styles.rpeLabel, rpe === n && styles.rpeLabelSelected]}>
                      {n}
                    </Text>
                  </Pressable>
                ))}
              </View>
            </View>

            {/* Notas */}
            <View>
              <Text style={fieldStyles.label}>Notas</Text>
              <TextInput
                style={[fieldStyles.input, styles.notesInput]}
                value={notes}
                onChangeText={setNotes}
                placeholder="Como foi o treino?"
                placeholderTextColor={colors.textTertiary}
                multiline
                numberOfLines={3}
                textAlignVertical="top"
              />
            </View>
          </Card>

          {saveError ? (
            <Card variant="flat" padding="base" style={styles.errorCard}>
              <Text style={styles.errorText}>{saveError}</Text>
            </Card>
          ) : null}

          <View style={editStyles.actionRow}>
            <Button label="Cancelar" variant="ghost" onPress={onCancel} style={editStyles.actionBtn} />
            <Button label="Salvar" onPress={handleSave} loading={isSaving} style={editStyles.actionBtn} />
          </View>
        </ScrollView>
      </KeyboardAvoidingView>

      {/* iOS date picker modal — mesmo padrão de log-workout */}
      {Platform.OS === "ios" && (
        <Modal visible={showDatePicker} transparent animationType="slide" onRequestClose={() => setShowDatePicker(false)}>
          <Pressable style={styles.modalOverlay} onPress={() => setShowDatePicker(false)} />
          <View style={[styles.modalSheet, shadows.lg as ViewStyle]}>
            <View style={styles.modalPickerHeader}>
              <Pressable onPress={() => setShowDatePicker(false)}>
                <Text style={styles.modalCancel}>Cancelar</Text>
              </Pressable>
              <Text style={styles.modalPickerTitle}>Selecionar data</Text>
              <Pressable onPress={() => { setWorkoutDate(tempDate); setShowDatePicker(false); }}>
                <Text style={styles.modalConfirm}>Confirmar</Text>
              </Pressable>
            </View>
            <DateTimePicker
              value={tempDate}
              mode="date"
              display="inline"
              maximumDate={new Date()}
              onChange={(_: DateTimePickerEvent, d?: Date) => { if (d) setTempDate(d); }}
              locale="pt-BR"
              themeVariant="light"
            />
          </View>
        </Modal>
      )}
    </SafeAreaView>
  );
}
```

Adicionar helpers locais (reutilizados de `log-workout.tsx`) antes do componente principal:

```typescript
const pad = (n: number) => String(n).padStart(2, "0");

function dateToISO(d: Date): string {
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
}

function dateToDisplay(d: Date): string {
  return `${pad(d.getDate())}/${pad(d.getMonth() + 1)}/${d.getFullYear()}`;
}

function applyTimeMask(raw: string): string {
  const digits = raw.replace(/\D/g, "").slice(0, 4);
  if (digits.length <= 2) return digits;
  return `${digits.slice(0, 2)}:${digits.slice(2)}`;
}

function timeToSeconds(hhmm: string): number | null {
  const [h, m] = hhmm.split(":").map(Number);
  if (isNaN(h) || isNaN(m) || m >= 60) return null;
  return h * 3600 + m * 60;
}

function buildDatetime(isoDate: string, timeHHMM: string): string {
  const [h, m] = timeHHMM.split(":").map(Number);
  const d = new Date(`${isoDate}T00:00:00`);
  d.setHours(h, m, 0, 0);
  return (
    `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}` +
    `T${pad(d.getHours())}:${pad(d.getMinutes())}:00`
  );
}
```

Adicionar componentes internos `EditField` e `EditFormField` e novos styles:

```typescript
function EditField({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <View style={fieldStyles.container}>
      <Text style={fieldStyles.label}>{label}</Text>
      {children}
    </View>
  );
}

function EditFormField({
  label, placeholder, value, onChangeText, keyboardType, error,
}: {
  label: string;
  placeholder?: string;
  value: string;
  onChangeText: (t: string) => void;
  keyboardType?: "numeric" | "decimal-pad";
  error?: string;
}) {
  return (
    <View style={fieldStyles.container}>
      <Text style={fieldStyles.label}>{label}</Text>
      <TextInput
        style={[fieldStyles.input, error ? fieldStyles.inputError : null]}
        value={value}
        onChangeText={onChangeText}
        placeholder={placeholder}
        placeholderTextColor={colors.textTertiary}
        keyboardType={keyboardType ?? "default"}
      />
      {error ? <Text style={fieldStyles.error}>{error}</Text> : null}
    </View>
  );
}
```

Adicionar ao `StyleSheet` de `styles`:

```typescript
  row: { flexDirection: "row", gap: spacing.sm },
  rowField: { flex: 1 },
  rpeRow: { flexDirection: "row", gap: spacing.xs, flexWrap: "wrap", marginTop: spacing.xs },
  rpeChip: {
    width: 36, height: 36, borderRadius: radii.md, borderWidth: 1.5,
    borderColor: colors.border, alignItems: "center", justifyContent: "center",
    backgroundColor: colors.background,
  },
  rpeChipSelected: { borderColor: colors.accent, backgroundColor: colors.accentSoft },
  rpeLabel: { ...(typography.bodyStrong as TextStyle), color: colors.textSecondary },
  rpeLabelSelected: { color: colors.accent },
  notesInput: { height: 80, paddingTop: spacing.sm },
  errorCard: { borderColor: colors.danger, backgroundColor: colors.dangerSoft },
  modalSheet: {
    backgroundColor: colors.surface,
    borderTopLeftRadius: radii.xl,
    borderTopRightRadius: radii.xl,
    paddingBottom: spacing["3xl"],
  } as ViewStyle,
  modalPickerHeader: {
    flexDirection: "row", alignItems: "center", justifyContent: "space-between",
    paddingHorizontal: spacing.xl, paddingVertical: spacing.base,
    borderBottomWidth: 1, borderBottomColor: colors.border,
  },
  modalPickerTitle: { ...(typography.titleSm as TextStyle), color: colors.textPrimary },
  modalCancel: { ...(typography.body as TextStyle), color: colors.textSecondary },
  modalConfirm: { ...(typography.bodyStrong as TextStyle), color: colors.accent },
```

Adicionar `editStyles` e `fieldStyles`:

```typescript
const editStyles = StyleSheet.create({
  card: { gap: spacing.base },
  dateField: {
    height: 48, borderWidth: 1, borderColor: colors.borderStrong,
    borderRadius: radii.md, paddingHorizontal: spacing.md,
    justifyContent: "center", backgroundColor: colors.background,
  },
  dateText: { ...(typography.body as TextStyle), color: colors.textPrimary },
  actionRow: { flexDirection: "row", gap: spacing.sm },
  actionBtn: { flex: 1 },
});

const fieldStyles = StyleSheet.create({
  container: { gap: spacing.xs },
  label: { ...(typography.bodySm as TextStyle), color: colors.textSecondary, fontWeight: "500" },
  input: {
    height: 48, borderWidth: 1, borderColor: colors.borderStrong,
    borderRadius: radii.md, paddingHorizontal: spacing.md,
    ...(typography.body as TextStyle), color: colors.textPrimary,
    backgroundColor: colors.background,
  },
  inputError: { borderColor: colors.danger },
  error: { ...(typography.caption as TextStyle), color: colors.danger },
});
```

- [ ] **Verificar tipos**

```bash
cd mobile && npx tsc --noEmit 2>&1 | head -20
```

Expected: sem erros.

- [ ] **Commit final**

```bash
git add mobile/app/(app)/workout/[id].tsx
git commit -m "feat(screen): complete workout detail with edit mode and delete modal"
```

---

## Task 12: Verificação final

- [ ] **Rodar todos os testes de backend**

```bash
cd backend && uv run pytest tests/ -v
```

Expected: todos os testes passam.

- [ ] **Typecheck do frontend**

```bash
cd mobile && npx tsc --noEmit
```

Expected: sem output (zero erros).

- [ ] **Smoke test manual**
  1. Acessar aba "Histórico" → lista de treinos aparece
  2. Tocar em um treino → abre tela de detalhe com métricas
  3. Tocar no ícone de lápis → modo edit abre com campos preenchidos
  4. Alterar distância → Salvar → métricas atualizadas na view
  5. Cancelar edição → volta para view sem alterações
  6. Tocar "Excluir treino" → modal de confirmação aparece
  7. Cancelar modal → modal fecha, treino continua
  8. Confirmar exclusão → volta para histórico, treino removido da lista
