import { useCallback, useEffect, useMemo, useState } from "react";

import * as workoutService from "../services/workout-service";
import { useAuthStore } from "../stores/auth-store";
import type { SessionType, WorkoutLog } from "../types/api";
import { ApiError } from "../types/api";
import {
  computeDailyVolume,
  computeWeeklyStatsBySport,
  computeWeeklySummary,
  type DailyVolume,
  type WeeklyStatsBySport,
  type WeeklySummary,
} from "../utils/workout-stats";

interface DashboardErrors {
  suggestion: string | null;
  history: string | null;
}

interface UseDashboardDataReturn {
  suggestion: SessionType | null;
  summary: WeeklySummary | null;
  statsBySport: WeeklyStatsBySport | null;
  logs: WorkoutLog[];
  recentLogs: WorkoutLog[];
  isLoading: boolean;
  errors: DashboardErrors;
  refetch: () => void;
}

// Busca um volume maior de histórico para calcular os resumos semanais corretamente
const HISTORY_LIMIT = 50;

export function useDashboardData(): UseDashboardDataReturn {
  const athleteProfileId = useAuthStore((state) => state.athleteProfileId);

  const [suggestion, setSuggestion] = useState<SessionType | null>(null);
  const [suggestionLoading, setSuggestionLoading] = useState(false);
  const [suggestionError, setSuggestionError] = useState<string | null>(null);

  const [logs, setLogs] = useState<WorkoutLog[]>([]);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [historyError, setHistoryError] = useState<string | null>(null);

  const fetchSuggestion = useCallback(async () => {
    if (!athleteProfileId) return;
    setSuggestionLoading(true);
    setSuggestionError(null);
    try {
      const result = await workoutService.getSuggestion(athleteProfileId);
      setSuggestion(result.suggested_session_type);
    } catch (err) {
      setSuggestionError(
        err instanceof ApiError ? err.message : "Erro ao buscar sugestão",
      );
    } finally {
      setSuggestionLoading(false);
    }
  }, [athleteProfileId]);

  const fetchHistory = useCallback(async () => {
    if (!athleteProfileId) return;
    setHistoryLoading(true);
    setHistoryError(null);
    try {
      const result = await workoutService.getHistory({
        athleteProfileId,
        limit: HISTORY_LIMIT,
      });
      setLogs(result.logs);
    } catch (err) {
      setHistoryError(
        err instanceof ApiError ? err.message : "Erro ao carregar histórico",
      );
    } finally {
      setHistoryLoading(false);
    }
  }, [athleteProfileId]);

  const refetch = useCallback(() => {
    fetchSuggestion();
    fetchHistory();
  }, [fetchSuggestion, fetchHistory]);

  useEffect(() => {
    refetch();
  }, [refetch]);

  const now = useMemo(() => new Date(), []);
  const summary = useMemo(
    () => (logs.length > 0 ? computeWeeklySummary(logs, now) : null),
    [logs, now],
  );
  const statsBySport = useMemo(
    () => (logs.length > 0 ? computeWeeklyStatsBySport(logs, now) : null),
    [logs, now],
  );
  const dailyVolume = useMemo(
    () => (logs.length > 0 ? computeDailyVolume(logs, now) : null),
    [logs, now],
  );

  const isLoading = suggestionLoading || historyLoading;

  return {
    suggestion,
    summary,
    statsBySport,
    logs,
    recentLogs: logs.slice(0, 5),
    isLoading,
    errors: {
      suggestion: suggestionError,
      history: historyError,
    },
    refetch,
  };
}
