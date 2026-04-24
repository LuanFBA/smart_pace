import { Heart, Zap, Gauge } from "lucide-react-native";
import { StyleSheet, Text, View, type TextStyle } from "react-native";

import { colors, spacing, typography } from "../theme";
import type { WorkoutLog } from "../types/api";
import {
  formatDurationCompact,
  formatPace,
  formatRelativeDate,
  formatSpeed,
  metersToKm,
} from "../utils/format";
import { SESSION_TYPE_LABELS } from "../utils/session-labels";
import { sessionTypeToSport } from "../utils/workout-stats";
import { Card } from "./Card";

interface WorkoutCardProps {
  log: WorkoutLog;
}

export function WorkoutCard({ log }: WorkoutCardProps) {
  const isCycling = sessionTypeToSport(log.session_type) === "cycling";
  const typeLabel = SESSION_TYPE_LABELS[log.session_type] ?? log.session_type;

  const hasFooter =
    log.average_heart_rate != null ||
    log.perceived_exertion != null ||
    (isCycling && log.average_power_watts != null);

  return (
    <Card variant="flat" padding="base" style={styles.card}>
      <View style={styles.header}>
        <Text style={styles.date}>{formatRelativeDate(log.started_at)}</Text>
        <Text style={[styles.typeLabel, isCycling && styles.typeLabelCycling]}>
          {typeLabel}
        </Text>
      </View>

      <View style={styles.metricsRow}>
        <View style={styles.primaryMetric}>
          <Text style={styles.primaryValue}>
            {metersToKm(log.actual_distance_meters)}
          </Text>
          <Text style={styles.primaryUnit}>km</Text>
        </View>

        <View style={styles.divider} />

        <View style={styles.secondaryMetrics}>
          <Metric label="Tempo" value={formatDurationCompact(log.actual_duration_seconds)} />
          {isCycling ? (
            <Metric
              label="Velocidade"
              value={`${formatSpeed(log.actual_distance_meters, log.actual_duration_seconds)} km/h`}
            />
          ) : (
            <Metric
              label="Pace"
              value={`${formatPace(log.average_pace_seconds_per_km)}/km`}
            />
          )}
        </View>
      </View>

      {hasFooter && (
        <View style={styles.footer}>
          {log.average_heart_rate != null && (
            <View style={styles.chip}>
              <Heart color={colors.danger} size={13} strokeWidth={2.2} />
              <Text style={styles.chipText}>{log.average_heart_rate} bpm</Text>
            </View>
          )}
          {isCycling && log.average_power_watts != null && (
            <View style={styles.chip}>
              <Gauge color={colors.success} size={13} strokeWidth={2.2} />
              <Text style={styles.chipText}>{log.average_power_watts} W</Text>
            </View>
          )}
          {log.perceived_exertion != null && (
            <View style={styles.chip}>
              <Zap color={colors.warning} size={13} strokeWidth={2.2} />
              <Text style={styles.chipText}>
                Esforço {log.perceived_exertion}/10
              </Text>
            </View>
          )}
        </View>
      )}
    </Card>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <View style={styles.metric}>
      <Text style={styles.metricLabel}>{label}</Text>
      <Text style={styles.metricValue}>{value}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    marginBottom: spacing.md,
  },
  header: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: spacing.sm,
  },
  date: {
    ...(typography.caption as TextStyle),
    color: colors.textTertiary,
    textTransform: "uppercase",
    letterSpacing: 0.8,
  },
  typeLabel: {
    ...(typography.caption as TextStyle),
    color: colors.accent,
    fontWeight: "600",
  },
  typeLabelCycling: {
    color: colors.success,
  },
  metricsRow: {
    flexDirection: "row",
    alignItems: "center",
  },
  primaryMetric: {
    flexDirection: "row",
    alignItems: "baseline",
    gap: 4,
  },
  primaryValue: {
    ...(typography.metricLg as TextStyle),
    color: colors.textPrimary,
  },
  primaryUnit: {
    ...(typography.titleSm as TextStyle),
    color: colors.textSecondary,
  },
  divider: {
    width: 1,
    height: 32,
    backgroundColor: colors.border,
    marginHorizontal: spacing.base,
  },
  secondaryMetrics: {
    flex: 1,
    flexDirection: "row",
    justifyContent: "space-between",
  },
  metric: {
    alignItems: "flex-start",
  },
  metricLabel: {
    ...(typography.caption as TextStyle),
    color: colors.textTertiary,
    marginBottom: 2,
  },
  metricValue: {
    ...(typography.bodyStrong as TextStyle),
    color: colors.textPrimary,
  },
  footer: {
    flexDirection: "row",
    gap: spacing.sm,
    marginTop: spacing.md,
    flexWrap: "wrap",
  },
  chip: {
    flexDirection: "row",
    alignItems: "center",
    gap: 4,
    paddingHorizontal: spacing.sm,
    paddingVertical: 4,
    backgroundColor: colors.gray100,
    borderRadius: 999,
  },
  chipText: {
    ...(typography.caption as TextStyle),
    color: colors.textSecondary,
    fontWeight: "600",
  },
});
