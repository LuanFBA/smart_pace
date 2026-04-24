import type { SessionType, SportType, WorkoutLog } from "../types/api";

export interface WeeklySummary {
  totalDistanceMeters: number;
  totalDurationSeconds: number;
  sessionCount: number;
  // Pace médio ponderado pela distância (segundos/km) — null se sem dados
  averagePaceSecondsPerKm: number | null;
}

export interface ModalityStats {
  sport: SportType;
  totalDistanceMeters: number;
  totalDurationSeconds: number;
  sessionCount: number;
}

export interface WeeklyStatsBySport {
  running: ModalityStats;
  cycling: ModalityStats;
}

export function sessionTypeToSport(sessionType: SessionType | null | undefined): SportType {
  // Fallback defensivo: logs antigos no backend podem não carregar session_type
  return sessionType?.startsWith("cycling") ? "cycling" : "running";
}

export interface DailyVolume {
  // 0 = segunda-feira, 6 = domingo
  dayIndex: number;
  // Rótulo curto em pt-BR (S, T, Q, Q, S, S, D)
  label: string;
  // Data normalizada (início do dia, horário local)
  date: Date;
  distanceMeters: number;
}

// Rótulos pt-BR para Segunda a Domingo
const WEEK_LABELS = ["S", "T", "Q", "Q", "S", "S", "D"];
const MONTH_SHORT = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"];

// Retorna rótulo da semana ISO: "10–16 Abr" ou "28 Mar – 3 Abr"
export function weekRangeLabel(reference: Date): string {
  const monday = getMonday(reference);
  const sunday = new Date(monday);
  sunday.setDate(sunday.getDate() + 6);
  const s = monday.getDate();
  const e = sunday.getDate();
  if (monday.getMonth() === sunday.getMonth()) {
    return `${s}–${e} ${MONTH_SHORT[monday.getMonth()]}`;
  }
  return `${s} ${MONTH_SHORT[monday.getMonth()]} – ${e} ${MONTH_SHORT[sunday.getMonth()]}`;
}

// Normaliza data para início do dia (00:00 local)
function startOfDay(date: Date): Date {
  return new Date(date.getFullYear(), date.getMonth(), date.getDate());
}

// Retorna a segunda-feira da semana ISO que contém `date`
function getMonday(date: Date): Date {
  const d = startOfDay(date);
  const day = d.getDay(); // 0=Dom, 1=Seg, ..., 6=Sáb
  const diff = day === 0 ? -6 : 1 - day;
  d.setDate(d.getDate() + diff);
  return d;
}

// Calcula agregados dos treinos da semana ISO (segunda a domingo)
export function computeWeeklySummary(
  logs: WorkoutLog[],
  reference: Date = new Date(),
): WeeklySummary {
  const monday = getMonday(reference);
  const sunday = new Date(monday);
  sunday.setDate(sunday.getDate() + 6);

  let totalDistanceMeters = 0;
  let totalDurationSeconds = 0;
  let weightedPaceAccumulator = 0;
  let sessionCount = 0;

  for (const log of logs) {
    const logDay = startOfDay(new Date(log.started_at));
    if (logDay < monday || logDay > sunday) continue;

    sessionCount += 1;
    totalDistanceMeters += log.actual_distance_meters;
    totalDurationSeconds += log.actual_duration_seconds;
    weightedPaceAccumulator +=
      log.average_pace_seconds_per_km * log.actual_distance_meters;
  }

  const averagePaceSecondsPerKm =
    totalDistanceMeters > 0
      ? weightedPaceAccumulator / totalDistanceMeters
      : null;

  return {
    totalDistanceMeters,
    totalDurationSeconds,
    sessionCount,
    averagePaceSecondsPerKm,
  };
}

// Agrega estatísticas da semana separando corrida e ciclismo
export function computeWeeklyStatsBySport(
  logs: WorkoutLog[],
  reference: Date = new Date(),
): WeeklyStatsBySport {
  const monday = getMonday(reference);
  const sunday = new Date(monday);
  sunday.setDate(sunday.getDate() + 6);

  const init = (sport: SportType): ModalityStats => ({
    sport,
    totalDistanceMeters: 0,
    totalDurationSeconds: 0,
    sessionCount: 0,
  });

  const result: WeeklyStatsBySport = {
    running: init("running"),
    cycling: init("cycling"),
  };

  for (const log of logs) {
    const logDay = startOfDay(new Date(log.started_at));
    if (logDay < monday || logDay > sunday) continue;
    const bucket = result[sessionTypeToSport(log.session_type)];
    bucket.totalDistanceMeters += log.actual_distance_meters;
    bucket.totalDurationSeconds += log.actual_duration_seconds;
    bucket.sessionCount += 1;
  }

  return result;
}

// Chave canônica de dia local (YYYY-M-D) para comparações
function dateKey(date: Date): string {
  return `${date.getFullYear()}-${date.getMonth()}-${date.getDate()}`;
}

// Conta dias consecutivos treinados até hoje (ou até ontem, como período de graça)
// Zera se não houver treino em "hoje" nem em "ontem"
export function computeCurrentStreak(
  logs: WorkoutLog[],
  reference: Date = new Date(),
): number {
  if (logs.length === 0) return 0;

  const trainedDays = new Set<string>();
  for (const log of logs) {
    trainedDays.add(dateKey(startOfDay(new Date(log.started_at))));
  }

  const today = startOfDay(reference);
  const yesterday = new Date(today);
  yesterday.setDate(yesterday.getDate() - 1);

  let cursor: Date;
  if (trainedDays.has(dateKey(today))) {
    cursor = today;
  } else if (trainedDays.has(dateKey(yesterday))) {
    cursor = yesterday;
  } else {
    return 0;
  }

  let streak = 0;
  while (trainedDays.has(dateKey(cursor))) {
    streak += 1;
    cursor.setDate(cursor.getDate() - 1);
  }
  return streak;
}

// Retorna array de 7 posições representando volume diário (km) de Seg a Dom da semana atual
export function computeDailyVolume(
  logs: WorkoutLog[],
  reference: Date = new Date(),
): DailyVolume[] {
  const monday = getMonday(reference);

  // Inicializa os 7 buckets: segunda (0) até domingo (6)
  const buckets: DailyVolume[] = Array.from({ length: 7 }, (_, index) => {
    const date = new Date(monday);
    date.setDate(date.getDate() + index);
    return {
      dayIndex: index,
      label: WEEK_LABELS[index],
      date,
      distanceMeters: 0,
    };
  });

  for (const log of logs) {
    const logDay = startOfDay(new Date(log.started_at));
    const diff = Math.floor(
      (logDay.getTime() - monday.getTime()) / (1000 * 60 * 60 * 24),
    );
    if (diff >= 0 && diff < 7) {
      buckets[diff].distanceMeters += log.actual_distance_meters;
    }
  }

  return buckets;
}
