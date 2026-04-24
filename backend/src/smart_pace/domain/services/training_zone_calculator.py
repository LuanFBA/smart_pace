from __future__ import annotations

from smart_pace.domain.value_objects.heart_rate import HeartRate, HeartRateZone

# Zonas de treino baseadas na fórmula de Karvonen
# Percentuais da FC de reserva (FCmax - FCrepouso)
_ZONE_DEFINITIONS: list[tuple[str, float, float]] = [
    ("Recovery", 0.50, 0.60),
    ("Aerobic", 0.60, 0.70),
    ("Tempo", 0.70, 0.80),
    ("Threshold", 0.80, 0.90),
    ("VO2max", 0.90, 1.00),
]


def compute_heart_rate_zones(
    maximum_heart_rate: HeartRate,
    resting_heart_rate: HeartRate,
) -> list[HeartRateZone]:
    """Calcula 5 zonas de FC usando a fórmula de Karvonen.

    Zona alvo = FCrepouso + (FCmax - FCrepouso) * percentual
    """
    reserve = maximum_heart_rate.beats_per_minute - resting_heart_rate.beats_per_minute

    zones: list[HeartRateZone] = []
    for name, lower_pct, upper_pct in _ZONE_DEFINITIONS:
        min_bpm = round(resting_heart_rate.beats_per_minute + reserve * lower_pct)
        max_bpm = round(resting_heart_rate.beats_per_minute + reserve * upper_pct)
        zones.append(HeartRateZone(name=name, min_bpm=min_bpm, max_bpm=max_bpm))

    return zones
