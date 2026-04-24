"""Modelos ORM do SQLAlchemy — camada de persistência.

Estes modelos NÃO são entidades do domínio. A conversão
entre ORM ↔ domínio é feita explicitamente nos mappers.
"""

from __future__ import annotations

import uuid
from datetime import UTC, date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    Uuid,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


# ──────────────────────────────────────────
# Users
# ──────────────────────────────────────────


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(256), nullable=False)
    full_name: Mapped[str] = mapped_column(String(256), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )


# ──────────────────────────────────────────
# Athlete Profiles
# ──────────────────────────────────────────


class AthleteProfileModel(Base):
    __tablename__ = "athlete_profiles"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id"), unique=True, nullable=False
    )
    sport_type: Mapped[str] = mapped_column(String(32), nullable=False)
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)
    resting_heart_rate_bpm: Mapped[int] = mapped_column(Integer, nullable=False)
    maximum_heart_rate_bpm: Mapped[int] = mapped_column(Integer, nullable=False)
    functional_threshold_power: Mapped[int | None] = mapped_column(Integer)
    current_vo2max: Mapped[float | None] = mapped_column(Float)
    training_experience_years: Mapped[int] = mapped_column(Integer, default=0)
    weekly_target_hours: Mapped[float] = mapped_column(Float, default=0.0)


# ──────────────────────────────────────────
# Training Plans
# ──────────────────────────────────────────


class TrainingPlanModel(Base):
    __tablename__ = "training_plans"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    athlete_profile_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("athlete_profiles.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    goal_description: Mapped[str] = mapped_column(Text, nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    sport_type: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="draft", nullable=False)


# ──────────────────────────────────────────
# Training Blocks
# ──────────────────────────────────────────


class TrainingBlockModel(Base):
    __tablename__ = "training_blocks"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    training_plan_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("training_plans.id"), nullable=False
    )
    week_number: Mapped[int] = mapped_column(Integer, nullable=False)
    phase: Mapped[str] = mapped_column(String(32), nullable=False)
    target_weekly_distance_meters: Mapped[int] = mapped_column(Integer, nullable=False)
    target_weekly_duration_seconds: Mapped[int] = mapped_column(
        Integer, nullable=False
    )


# ──────────────────────────────────────────
# Workout Sessions
# ──────────────────────────────────────────


class WorkoutSessionModel(Base):
    __tablename__ = "workout_sessions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    athlete_profile_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("athlete_profiles.id"), nullable=False
    )
    scheduled_date: Mapped[date] = mapped_column(Date, nullable=False)
    session_type: Mapped[str] = mapped_column(String(32), nullable=False)
    training_block_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("training_blocks.id")
    )
    target_distance_meters: Mapped[int | None] = mapped_column(Integer)
    target_duration_seconds: Mapped[int | None] = mapped_column(Integer)
    target_min_pace_sec_per_km: Mapped[int | None] = mapped_column(Integer)
    target_max_pace_sec_per_km: Mapped[int | None] = mapped_column(Integer)
    # Zona de FC alvo armazenada como JSONB: {"name": str, "min_bpm": int, "max_bpm": int}
    target_heart_rate_zone: Mapped[dict | None] = mapped_column(JSONB)  # type: ignore[type-arg]
    status: Mapped[str] = mapped_column(
        String(32), default="scheduled", nullable=False
    )


# ──────────────────────────────────────────
# Workout Logs
# ──────────────────────────────────────────


class WorkoutLogModel(Base):
    __tablename__ = "workout_logs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    workout_session_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("workout_sessions.id"), unique=True, nullable=False
    )
    athlete_profile_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("athlete_profiles.id"), nullable=False
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    finished_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    actual_distance_meters: Mapped[int] = mapped_column(Integer, nullable=False)
    actual_duration_seconds: Mapped[int] = mapped_column(Integer, nullable=False)
    average_pace_sec_per_km: Mapped[int] = mapped_column(Integer, nullable=False)
    average_heart_rate_bpm: Mapped[int | None] = mapped_column(Integer)
    maximum_heart_rate_bpm: Mapped[int | None] = mapped_column(Integer)
    perceived_exertion: Mapped[int | None] = mapped_column(Integer)
    notes: Mapped[str | None] = mapped_column(Text)
    average_power_watts: Mapped[int | None] = mapped_column(Integer)  # Potência média — ciclismo


# ──────────────────────────────────────────
# Performance Metrics
# ──────────────────────────────────────────


class PerformanceMetricsModel(Base):
    __tablename__ = "performance_metrics"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    athlete_profile_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("athlete_profiles.id"), nullable=False
    )
    calculated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    estimated_vo2max: Mapped[float] = mapped_column(Float, nullable=False)
    # Zonas de FC armazenadas como JSONB: [{"name": str, "min_bpm": int, "max_bpm": int}]
    heart_rate_zones: Mapped[list] = mapped_column(JSONB, nullable=False)  # type: ignore[type-arg]
    lactate_threshold_pace_sec_per_km: Mapped[int | None] = mapped_column(Integer)
    chronic_training_load: Mapped[float] = mapped_column(Float, default=0.0)
    acute_training_load: Mapped[float] = mapped_column(Float, default=0.0)
