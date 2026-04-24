import { useCallback, useMemo, useState } from "react";
import {
  RefreshControl,
  ScrollView,
  StyleSheet,
  Text,
  View,
  type TextStyle,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { router, useFocusEffect } from "expo-router";

import { Card } from "../../../src/components/Card";
import { NextWorkoutCard } from "../../../src/components/dashboard/NextWorkoutCard";
import { WeeklyStatsStrip } from "../../../src/components/dashboard/WeeklyStatsStrip";
import { WeeklyStreakCard } from "../../../src/components/dashboard/WeeklyStreakCard";
import { WeeklyVolumeChart } from "../../../src/components/dashboard/WeeklyVolumeChart";
import { useDashboardData } from "../../../src/hooks/use-dashboard-data";
import { useAuthStore } from "../../../src/stores/auth-store";
import { colors, spacing, typography } from "../../../src/theme";
import {
  computeCurrentStreak,
  computeDailyVolume,
  weekRangeLabel,
} from "../../../src/utils/workout-stats";

export default function DashboardScreen() {
  const athleteProfileId = useAuthStore((state) => state.athleteProfileId);

  const {
    suggestion,
    statsBySport,
    logs,
    isLoading,
    errors,
    refetch,
  } = useDashboardData();

  // Recarrega os dados sempre que a tela volta a ficar em foco
  useFocusEffect(
    useCallback(() => {
      refetch();
    }, [refetch]),
  );

  // weekOffset: 0 = semana atual, -1 = semana anterior, etc.
  const [weekOffset, setWeekOffset] = useState(0);

  // Data de referência para o gráfico de volume
  const referenceDate = useMemo(() => {
    const d = new Date();
    d.setDate(d.getDate() + weekOffset * 7);
    return d;
  }, [weekOffset]);

  // Volume diário recomputado a cada mudança de semana
  const dailyVolume = useMemo(
    () => (logs.length > 0 ? computeDailyVolume(logs, referenceDate) : null),
    [logs, referenceDate],
  );

  const chartWeekLabel = useMemo(() => weekRangeLabel(referenceDate), [referenceDate]);

  // Frequência e streak sempre baseados na semana atual (independente da navegação do gráfico)
  const currentWeekDays = useMemo(
    () => (logs.length > 0 ? computeDailyVolume(logs, new Date()) : null),
    [logs],
  );
  const currentStreak = useMemo(() => computeCurrentStreak(logs), [logs]);

  return (
    <SafeAreaView style={styles.root}>
      <ScrollView
        contentContainerStyle={styles.content}
        showsVerticalScrollIndicator={false}
        refreshControl={
          <RefreshControl
            refreshing={isLoading}
            onRefresh={refetch}
            tintColor={colors.accent}
          />
        }
      >
        <View style={styles.sections}>
          <WeeklyStatsStrip
            stats={statsBySport}
            isLoading={isLoading && statsBySport === null}
          />

          <WeeklyStreakCard
            days={currentWeekDays}
            streak={currentStreak}
            isLoading={isLoading && currentWeekDays === null}
          />

          <Section title="Sugestão de próximo treino">
            <NextWorkoutCard
              sessionType={suggestion}
              isLoading={isLoading && suggestion === null && errors.suggestion === null}
              hasProfile={Boolean(athleteProfileId)}
              error={errors.suggestion}
              onRetry={refetch}
              onCreateProfile={() => router.push("/(app)/create-profile")}
            />
          </Section>

          <Section title="Volume semanal">
            <Card variant="flat" padding="base">
              <WeeklyVolumeChart
                data={dailyVolume}
                isLoading={isLoading && dailyVolume === null}
                weekLabel={chartWeekLabel}
                canGoNext={weekOffset < 0}
                onPrevWeek={() => setWeekOffset((o) => o - 1)}
                onNextWeek={() => setWeekOffset((o) => o + 1)}
              />
            </Card>
          </Section>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

function Section({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <View style={sectionStyles.container}>
      <Text style={sectionStyles.title}>{title}</Text>
      {children}
    </View>
  );
}

const styles = StyleSheet.create({
  root: {
    flex: 1,
    backgroundColor: colors.background,
  },
  content: {
    paddingBottom: spacing["3xl"],
  },
  sections: {
    paddingHorizontal: spacing.xl,
    paddingTop: spacing.xl,
    gap: spacing["2xl"],
  },
});

const sectionStyles = StyleSheet.create({
  container: {
    gap: spacing.md,
  },
  title: {
    ...(typography.titleMd as TextStyle),
    color: colors.textPrimary,
  },
});
