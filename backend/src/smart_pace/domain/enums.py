from __future__ import annotations

from enum import Enum


class SportType(str, Enum):
    RUNNING = "running"
    CYCLING = "cycling"


class TrainingPlanStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TrainingPhase(str, Enum):
    BASE = "base"
    BUILD = "build"
    PEAK = "peak"
    TAPER = "taper"
    RECOVERY = "recovery"


class SessionType(str, Enum):
    EASY_RUN = "easy_run"
    TEMPO = "tempo"
    INTERVAL = "interval"
    LONG_RUN = "long_run"
    RECOVERY = "recovery"
    CYCLING_ENDURANCE = "cycling_endurance"
    CYCLING_INTERVAL = "cycling_interval"


class SessionStatus(str, Enum):
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    PARTIAL = "partial"
