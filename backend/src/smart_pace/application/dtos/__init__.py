from smart_pace.application.dtos.auth import (
    AuthTokensOutput,
    DeactivateAccountInput,
    LoginInput,
    RefreshTokenInput,
    RegisterUserInput,
    UserOutput,
)
from smart_pace.application.dtos.metrics import (
    PerformanceDashboardOutput,
    ViewPerformanceDashboardInput,
)
from smart_pace.application.dtos.profile import (
    AthleteProfileOutput,
    CreateAthleteProfileInput,
    GetProfileByUserIdInput,
    HeartRateZoneOutput,
    UpdateHeartRateDataInput,
    ViewHeartRateZonesInput,
)
from smart_pace.application.dtos.training_plan import (
    ActivateTrainingPlanInput,
    CancelTrainingPlanInput,
    CreateTrainingPlanInput,
    GetTrainingPlanInput,
    ListTrainingPlansInput,
    TrainingPlanOutput,
)
from smart_pace.application.dtos.workout import (
    GetNextWorkoutSuggestionInput,
    LogWorkoutInput,
    ScheduleWorkoutSessionInput,
    ViewWorkoutHistoryInput,
    WorkoutHistoryOutput,
    WorkoutLogOutput,
    WorkoutSessionOutput,
    WorkoutSuggestionOutput,
)

__all__ = [
    "ActivateTrainingPlanInput",
    "AthleteProfileOutput",
    "AuthTokensOutput",
    "CancelTrainingPlanInput",
    "CreateAthleteProfileInput",
    "CreateTrainingPlanInput",
    "DeactivateAccountInput",
    "GetNextWorkoutSuggestionInput",
    "GetProfileByUserIdInput",
    "GetTrainingPlanInput",
    "HeartRateZoneOutput",
    "ListTrainingPlansInput",
    "LogWorkoutInput",
    "LoginInput",
    "PerformanceDashboardOutput",
    "RefreshTokenInput",
    "RegisterUserInput",
    "ScheduleWorkoutSessionInput",
    "TrainingPlanOutput",
    "UpdateHeartRateDataInput",
    "UserOutput",
    "ViewHeartRateZonesInput",
    "ViewPerformanceDashboardInput",
    "ViewWorkoutHistoryInput",
    "WorkoutHistoryOutput",
    "WorkoutLogOutput",
    "WorkoutSessionOutput",
    "WorkoutSuggestionOutput",
]
