import { useCallback, useEffect, useState } from "react";

import * as workoutService from "../services/workout-service";
import { useAuthStore } from "../stores/auth-store";
import type { WorkoutLog } from "../types/api";
import { ApiError } from "../types/api";

interface UseWorkoutHistoryReturn {
  logs: WorkoutLog[];
  totalCount: number;
  isLoading: boolean;
  error: string | null;
  refetch: () => void;
}

export function useWorkoutHistory(limit = 5): UseWorkoutHistoryReturn {
  const [logs, setLogs] = useState<WorkoutLog[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const athleteProfileId = useAuthStore((state) => state.athleteProfileId);

  const fetchHistory = useCallback(async () => {
    if (!athleteProfileId) return;

    setIsLoading(true);
    setError(null);
    try {
      const result = await workoutService.getHistory({
        athleteProfileId,
        limit,
      });
      setLogs(result.logs);
      setTotalCount(result.total_count);
    } catch (err) {
      const message =
        err instanceof ApiError ? err.message : "Erro ao carregar histórico";
      setError(message);
    } finally {
      setIsLoading(false);
    }
  }, [athleteProfileId, limit]);

  useEffect(() => {
    fetchHistory();
  }, [fetchHistory]);

  return { logs, totalCount, isLoading, error, refetch: fetchHistory };
}
