import { useCallback, useEffect, useState } from "react";
import {
  ActivityIndicator,
  FlatList,
  RefreshControl,
  StyleSheet,
  Text,
  type TextStyle,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { Dumbbell } from "lucide-react-native";

import { WorkoutCard } from "../../../src/components/WorkoutCard";
import { Skeleton } from "../../../src/components/Skeleton";
import { useAuthStore } from "../../../src/stores/auth-store";
import { getHistory } from "../../../src/services/workout-service";
import { ApiError } from "../../../src/types/api";
import type { WorkoutLog } from "../../../src/types/api";
import { colors, spacing, typography } from "../../../src/theme";

const PAGE_SIZE = 20;

export default function ActivityHistoryScreen() {
  const athleteProfileId = useAuthStore((state) => state.athleteProfileId);

  const [logs, setLogs] = useState<WorkoutLog[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchPage = useCallback(
    async (offset: number, replace: boolean) => {
      if (!athleteProfileId) return;
      try {
        const result = await getHistory({
          athleteProfileId,
          limit: PAGE_SIZE,
          offset,
        });
        setTotalCount(result.total_count);
        setLogs((prev) =>
          replace ? result.logs : [...prev, ...result.logs],
        );
      } catch (err) {
        setError(
          err instanceof ApiError ? err.message : "Erro ao carregar histórico",
        );
      }
    },
    [athleteProfileId],
  );

  // Carga inicial
  useEffect(() => {
    setIsLoading(true);
    setError(null);
    fetchPage(0, true).finally(() => setIsLoading(false));
  }, [fetchPage]);

  // Pull-to-refresh
  const handleRefresh = useCallback(async () => {
    setIsRefreshing(true);
    setError(null);
    await fetchPage(0, true);
    setIsRefreshing(false);
  }, [fetchPage]);

  // Carrega próxima página ao chegar no fim da lista
  const handleLoadMore = useCallback(async () => {
    if (isLoadingMore || logs.length >= totalCount) return;
    setIsLoadingMore(true);
    await fetchPage(logs.length, false);
    setIsLoadingMore(false);
  }, [isLoadingMore, logs.length, totalCount, fetchPage]);

  // --- Estados de tela inteira ---

  if (isLoading) {
    return (
      <SafeAreaView style={styles.root}>
        <Text style={styles.screenTitle}>Histórico de treinos</Text>
        {Array.from({ length: 5 }).map((_, i) => (
          <Skeleton key={i} height={100} style={styles.skeletonItem} />
        ))}
      </SafeAreaView>
    );
  }

  if (error) {
    return (
      <SafeAreaView style={styles.centered}>
        <Text style={styles.errorText}>{error}</Text>
      </SafeAreaView>
    );
  }

  if (logs.length === 0) {
    return (
      <SafeAreaView style={styles.centered}>
        <Dumbbell color={colors.textTertiary} size={40} strokeWidth={1.5} />
        <Text style={styles.emptyTitle}>Nenhum treino registrado</Text>
        <Text style={styles.emptySubtitle}>
          Registre seu primeiro treino para ver o histórico aqui.
        </Text>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.root}>
      <FlatList
        data={logs}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => <WorkoutCard log={item} />}
        contentContainerStyle={styles.listContent}
        showsVerticalScrollIndicator={false}
        refreshControl={
          <RefreshControl
            refreshing={isRefreshing}
            onRefresh={handleRefresh}
            tintColor={colors.accent}
          />
        }
        onEndReached={handleLoadMore}
        onEndReachedThreshold={0.3}
        ListHeaderComponent={
          <>
            <Text style={styles.screenTitle}>Histórico de treinos</Text>
            <Text style={styles.countLabel}>
              {totalCount} {totalCount === 1 ? "treino" : "treinos"} no total
            </Text>
          </>
        }
        ListFooterComponent={
          isLoadingMore ? (
            <ActivityIndicator
              color={colors.accent}
              style={styles.footerSpinner}
            />
          ) : null
        }
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  root: {
    flex: 1,
    backgroundColor: colors.background,
  },
  listContent: {
    paddingHorizontal: spacing.xl,
    paddingTop: spacing.lg,
    paddingBottom: spacing["3xl"],
  },
  // --- Skeleton ---
  skeletonItem: {
    marginHorizontal: spacing.xl,
    marginBottom: spacing.md,
    borderRadius: 10,
  },
  // --- Estados centralizados ---
  centered: {
    flex: 1,
    backgroundColor: colors.background,
    alignItems: "center",
    justifyContent: "center",
    paddingHorizontal: spacing["2xl"],
    gap: spacing.sm,
  },
  errorText: {
    ...(typography.bodySm as TextStyle),
    color: colors.danger,
    textAlign: "center",
  },
  emptyTitle: {
    ...(typography.titleSm as TextStyle),
    color: colors.textPrimary,
    textAlign: "center",
    marginTop: spacing.sm,
  },
  emptySubtitle: {
    ...(typography.bodySm as TextStyle),
    color: colors.textSecondary,
    textAlign: "center",
    lineHeight: 20,
  },
  // --- Header e footer da lista ---
  screenTitle: {
    ...(typography.titleLg as TextStyle),
    color: colors.textPrimary,
    marginBottom: spacing.sm,
  },
  countLabel: {
    ...(typography.caption as TextStyle),
    color: colors.textTertiary,
    textTransform: "uppercase",
    letterSpacing: 0.8,
    fontWeight: "600",
    marginBottom: spacing.base,
  },
  footerSpinner: {
    marginTop: spacing.lg,
  },
});
