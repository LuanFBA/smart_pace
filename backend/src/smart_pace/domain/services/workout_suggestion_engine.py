from __future__ import annotations

from smart_pace.domain.entities.athlete_profile import AthleteProfile
from smart_pace.domain.entities.workout_session import WorkoutSession
from smart_pace.domain.enums import SessionType, SportType

# Mapeamento de sessão anterior → próxima sessão sugerida (corrida)
_RUNNING_NEXT_SESSION: dict[SessionType, SessionType] = {
    SessionType.INTERVAL: SessionType.RECOVERY,
    SessionType.TEMPO: SessionType.EASY_RUN,
    SessionType.LONG_RUN: SessionType.RECOVERY,
    SessionType.EASY_RUN: SessionType.TEMPO,
    SessionType.RECOVERY: SessionType.EASY_RUN,
}

# Mapeamento para ciclismo
_CYCLING_NEXT_SESSION: dict[SessionType, SessionType] = {
    SessionType.CYCLING_INTERVAL: SessionType.RECOVERY,
    SessionType.CYCLING_ENDURANCE: SessionType.CYCLING_INTERVAL,
    SessionType.RECOVERY: SessionType.CYCLING_ENDURANCE,
}


def suggest_next_session_type(
    athlete_profile: AthleteProfile,
    recent_sessions: list[WorkoutSession],
) -> SessionType:
    """Sugere o tipo do próximo treino baseado no histórico recente.

    Regras:
    - Após treino intenso (interval/tempo/long_run) → recuperação ou leve
    - Após treino leve → pode intensificar
    - Sem histórico → começa com treino leve
    """
    if athlete_profile.sport_type == SportType.RUNNING:
        session_map = _RUNNING_NEXT_SESSION
        default = SessionType.EASY_RUN
    else:
        session_map = _CYCLING_NEXT_SESSION
        default = SessionType.CYCLING_ENDURANCE

    if not recent_sessions:
        return default

    last_session_type = recent_sessions[0].session_type
    return session_map.get(last_session_type, default)
