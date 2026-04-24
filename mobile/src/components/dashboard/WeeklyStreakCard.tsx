import { Flame } from "lucide-react-native";
import { StyleSheet, Text, View, type TextStyle } from "react-native";

import { Card } from "../Card";
import { Skeleton } from "../Skeleton";
import { colors, spacing, typography } from "../../theme";
import type { DailyVolume } from "../../utils/workout-stats";

interface WeeklyStreakCardProps {
  days: DailyVolume[] | null;
  streak: number;
  isLoading?: boolean;
}

function startOfDay(date: Date): number {
  return new Date(date.getFullYear(), date.getMonth(), date.getDate()).getTime();
}

export function WeeklyStreakCard({
  days,
  streak,
  isLoading = false,
}: WeeklyStreakCardProps) {
  const showSkeleton = isLoading || days === null;

  const trainedThisWeek = days
    ? days.filter((d) => d.distanceMeters > 0).length
    : 0;

  return (
    <Card variant="flat" padding="md" style={styles.card}>
      <View style={styles.header}>
        <View style={styles.headerLeft}>
          <Text style={styles.headerTitle}>Sequência</Text>
          <Text style={styles.headerSubtitle}>
            {showSkeleton
              ? " "
              : `${trainedThisWeek}/7 dias na semana`}
          </Text>
        </View>

        <View style={styles.streakBadge}>
          <Flame
            color={streak > 0 ? colors.warning : colors.textTertiary}
            size={18}
            strokeWidth={2}
            fill={streak > 0 ? colors.warning : "transparent"}
          />
          <Text
            style={[
              styles.streakValue,
              streak > 0 && styles.streakValueActive,
            ]}
          >
            {showSkeleton ? "–" : String(streak)}
          </Text>
        </View>
      </View>

      {showSkeleton ? (
        <Skeleton height={36} />
      ) : (
        <DayDots days={days} />
      )}
    </Card>
  );
}

function DayDots({ days }: { days: DailyVolume[] }) {
  const todayStart = startOfDay(new Date());

  return (
    <View style={styles.dotsRow}>
      {days.map((d) => {
        const dayStart = startOfDay(d.date);
        const isToday = dayStart === todayStart;
        const isFuture = dayStart > todayStart;
        const trained = d.distanceMeters > 0;

        return (
          <View key={d.dayIndex} style={styles.dotCell}>
            <View
              style={[
                styles.dot,
                trained && styles.dotTrained,
                !trained && isFuture && styles.dotFuture,
                isToday && styles.dotToday,
              ]}
            />
            <Text
              style={[
                styles.dayLabel,
                isToday && styles.dayLabelToday,
              ]}
            >
              {d.label}
            </Text>
          </View>
        );
      })}
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    gap: spacing.md,
  },
  header: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
  },
  headerLeft: {
    gap: 2,
  },
  headerTitle: {
    ...(typography.bodyStrong as TextStyle),
    color: colors.textPrimary,
  },
  headerSubtitle: {
    ...(typography.caption as TextStyle),
    color: colors.textTertiary,
  },
  streakBadge: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.xs,
  },
  streakValue: {
    ...(typography.titleMd as TextStyle),
    color: colors.textTertiary,
    fontWeight: "700",
  },
  streakValueActive: {
    color: colors.warning,
  },
  dotsRow: {
    flexDirection: "row",
    justifyContent: "space-between",
  },
  dotCell: {
    flex: 1,
    alignItems: "center",
    gap: spacing.xs,
  },
  dot: {
    width: 22,
    height: 22,
    borderRadius: 11,
    backgroundColor: "transparent",
    borderWidth: 1.5,
    borderColor: colors.border,
  },
  dotTrained: {
    backgroundColor: colors.accent,
    borderColor: colors.accent,
  },
  dotFuture: {
    borderStyle: "dashed",
  },
  dotToday: {
    borderWidth: 2,
    borderColor: colors.accent,
  },
  dayLabel: {
    ...(typography.caption as TextStyle),
    color: colors.textTertiary,
  },
  dayLabelToday: {
    color: colors.accent,
    fontWeight: "700",
  },
});
