import { Bike, Footprints } from "lucide-react-native";
import { StyleSheet, Text, View, type TextStyle } from "react-native";

import { Card } from "../../components/Card";
import { Skeleton } from "../../components/Skeleton";
import { colors, spacing, typography } from "../../theme";
import { formatDurationCompact, metersToKm } from "../../utils/format";
import type { ModalityStats, WeeklyStatsBySport } from "../../utils/workout-stats";

interface WeeklyStatsStripProps {
  stats: WeeklyStatsBySport | null;
  isLoading?: boolean;
}

export function WeeklyStatsStrip({ stats, isLoading = false }: WeeklyStatsStripProps) {
  return (
    <View style={styles.row}>
      <ModalityCard
        title="Corrida"
        icon={<Footprints color={colors.accent} size={18} strokeWidth={2} />}
        tintColor={colors.accent}
        data={stats?.running ?? null}
        isLoading={isLoading}
      />
      <ModalityCard
        title="Ciclismo"
        icon={<Bike color={colors.success} size={18} strokeWidth={2} />}
        tintColor={colors.success}
        data={stats?.cycling ?? null}
        isLoading={isLoading}
      />
    </View>
  );
}

function ModalityCard({
  title,
  icon,
  tintColor,
  data,
  isLoading,
}: {
  title: string;
  icon: React.ReactNode;
  tintColor: string;
  data: ModalityStats | null;
  isLoading: boolean;
}) {
  const showSkeleton = isLoading || data === null;

  return (
    <Card variant="flat" padding="md" style={styles.card}>
      <View style={styles.header}>
        {icon}
        <Text style={styles.title} numberOfLines={1}>
          {title}
        </Text>
      </View>

      {showSkeleton ? (
        <>
          <Skeleton height={20} width="80%" style={styles.skeletonLine} />
          <Skeleton height={14} width="60%" style={styles.skeletonLine} />
          <Skeleton height={14} width="55%" />
        </>
      ) : (
        <>
          <Text style={[styles.primary, { color: tintColor }]}>
            {metersToKm(data.totalDistanceMeters)} km
          </Text>
          <StatRow
            label="Tempo"
            value={
              data.totalDurationSeconds > 0
                ? formatDurationCompact(data.totalDurationSeconds)
                : "—"
            }
          />
          <StatRow
            label="Sessões"
            value={String(data.sessionCount)}
          />
        </>
      )}
    </Card>
  );
}

function StatRow({ label, value }: { label: string; value: string }) {
  return (
    <View style={styles.statRow}>
      <Text style={styles.statLabel}>{label}</Text>
      <Text style={styles.statValue}>{value}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  row: {
    flexDirection: "row",
    gap: spacing.sm,
  },
  card: {
    flex: 1,
    gap: spacing.xs,
  },
  header: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.xs,
    marginBottom: spacing.xs,
  },
  title: {
    ...(typography.caption as TextStyle),
    color: colors.textTertiary,
    textTransform: "uppercase",
    letterSpacing: 0.6,
    flexShrink: 1,
  },
  primary: {
    ...(typography.titleMd as TextStyle),
    fontWeight: "700",
    marginBottom: spacing.xs,
  },
  statRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "baseline",
  },
  statLabel: {
    ...(typography.caption as TextStyle),
    color: colors.textTertiary,
  },
  statValue: {
    ...(typography.bodySm as TextStyle),
    color: colors.textPrimary,
    fontWeight: "600",
  },
  skeletonLine: {
    marginBottom: spacing.xs,
  },
});
