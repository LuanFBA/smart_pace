import { useRef } from "react";
import { StyleSheet, Text, View, type GestureResponderEvent, type TextStyle } from "react-native";
import { ChevronLeft, ChevronRight } from "lucide-react-native";
import { Pressable } from "react-native";
import Svg, { Rect } from "react-native-svg";

import { colors, radii, spacing, typography } from "../../theme";
import type { DailyVolume } from "../../utils/workout-stats";
import { Skeleton } from "../Skeleton";

interface WeeklyVolumeChartProps {
  data: DailyVolume[] | null;
  isLoading?: boolean;
  weekLabel: string;
  canGoNext: boolean;
  onPrevWeek: () => void;
  onNextWeek: () => void;
}

const CHART_HEIGHT = 80;
const BAR_COUNT = 7;
const MIN_BAR_HEIGHT = 4;
const SWIPE_THRESHOLD = 50;

function startOfDay(date: Date): number {
  return new Date(date.getFullYear(), date.getMonth(), date.getDate()).getTime();
}

function formatKm(meters: number): string {
  if (meters === 0) return "";
  const km = meters / 1000;
  return (km % 1 === 0 ? String(km) : km.toFixed(1)) + " km";
}

export function WeeklyVolumeChart({
  data,
  isLoading = false,
  weekLabel,
  canGoNext,
  onPrevWeek,
  onNextWeek,
}: WeeklyVolumeChartProps) {
  // Detecta swipe horizontal para navegar entre semanas
  const touchStartX = useRef(0);

  function onTouchStart(e: GestureResponderEvent) {
    touchStartX.current = e.nativeEvent.pageX;
  }

  function onTouchEnd(e: GestureResponderEvent) {
    const dx = e.nativeEvent.pageX - touchStartX.current;
    if (Math.abs(dx) < SWIPE_THRESHOLD) return;
    if (dx > 0) onPrevWeek();          // swipe direita → semana anterior
    else if (canGoNext) onNextWeek();  // swipe esquerda → próxima semana
  }

  if (isLoading || data === null) {
    return (
      <View style={styles.container}>
        <View style={styles.navRow}>
          <Skeleton width={80} height={14} />
        </View>
        <Skeleton height={CHART_HEIGHT} />
        <View style={styles.labelsRow}>
          {Array.from({ length: BAR_COUNT }).map((_, i) => (
            <Skeleton key={i} width={20} height={10} style={styles.labelSkeleton} />
          ))}
        </View>
      </View>
    );
  }

  const todayStart = startOfDay(new Date());
  const maxMeters = Math.max(...data.map((d) => d.distanceMeters), 1);
  const weekTotalMeters = data.reduce((acc, d) => acc + d.distanceMeters, 0);
  const weekTotalKm = weekTotalMeters > 0
    ? (weekTotalMeters / 1000).toFixed(1) + " km"
    : "0 km";

  return (
    <View style={styles.container}>
      {/* Navegação de semanas */}
      <View style={styles.navRow}>
        <Pressable
          style={styles.navButton}
          onPress={onPrevWeek}
          hitSlop={8}
        >
          <ChevronLeft color={colors.accent} size={18} strokeWidth={2} />
        </Pressable>

        <View style={styles.navCenter}>
          <Text style={styles.weekLabel}>{weekLabel}</Text>
          <Text style={styles.weekTotal}>{weekTotalKm}</Text>
        </View>

        <Pressable
          style={[styles.navButton, !canGoNext && styles.navButtonDisabled]}
          onPress={canGoNext ? onNextWeek : undefined}
          hitSlop={8}
        >
          <ChevronRight
            color={canGoNext ? colors.accent : colors.border}
            size={18}
            strokeWidth={2}
          />
        </Pressable>
      </View>

      {/* Gráfico com suporte a swipe */}
      <View onTouchStart={onTouchStart} onTouchEnd={onTouchEnd}>
        <ChartBars data={data} maxMeters={maxMeters} todayStart={todayStart} />
      </View>

      {/* Rótulos dos dias + km */}
      <View style={styles.labelsRow}>
        {data.map((d) => {
          const isToday = startOfDay(d.date) === todayStart;
          const km = formatKm(d.distanceMeters);
          return (
            <View key={d.dayIndex} style={styles.labelCell}>
              <Text style={[styles.dayLabel, isToday && styles.dayLabelToday]}>
                {d.label}
              </Text>
              <Text style={[styles.kmLabel, isToday && styles.kmLabelToday]} numberOfLines={1}>
                {km || " "}
              </Text>
            </View>
          );
        })}
      </View>
    </View>
  );
}

function ChartBars({
  data,
  maxMeters,
  todayStart,
}: {
  data: DailyVolume[];
  maxMeters: number;
  todayStart: number;
}) {
  const containerWidth = 340;
  const gap = 6;
  const barWidth = (containerWidth - gap * (BAR_COUNT - 1)) / BAR_COUNT;

  return (
    <Svg
      viewBox={`0 0 ${containerWidth} ${CHART_HEIGHT}`}
      height={CHART_HEIGHT}
      width="100%"
      preserveAspectRatio="none"
    >
      {data.map((d, index) => {
        const dayStart = startOfDay(d.date);
        const isToday = dayStart === todayStart;
        const isFuture = dayStart > todayStart;
        const hasVolume = d.distanceMeters > 0;

        const barHeight = hasVolume
          ? Math.max(MIN_BAR_HEIGHT, Math.round((d.distanceMeters / maxMeters) * CHART_HEIGHT))
          : MIN_BAR_HEIGHT;

        const x = index * (barWidth + gap);
        const y = CHART_HEIGHT - barHeight;

        const fill = isFuture
          ? colors.gray200
          : hasVolume
            ? isToday ? colors.accent : colors.accentSoft
            : colors.gray200;

        return (
          <Rect
            key={d.dayIndex}
            x={x}
            y={y}
            width={barWidth}
            height={barHeight}
            rx={radii.sm}
            ry={radii.sm}
            fill={fill}
          />
        );
      })}
    </Svg>
  );
}

const styles = StyleSheet.create({
  container: {
    gap: spacing.sm,
  },
  // --- Navegação ---
  navRow: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
  },
  navButton: {
    padding: spacing.xs,
  },
  navButtonDisabled: {
    opacity: 0.4,
  },
  navCenter: {
    alignItems: "center",
    gap: 1,
  },
  weekLabel: {
    ...(typography.bodyStrong as TextStyle),
    color: colors.textPrimary,
  },
  weekTotal: {
    ...(typography.caption as TextStyle),
    color: colors.textSecondary,
  },
  // --- Rótulos ---
  labelsRow: {
    flexDirection: "row",
    justifyContent: "space-between",
  },
  labelCell: {
    flex: 1,
    alignItems: "center",
    gap: 1,
  },
  dayLabel: {
    ...(typography.caption as TextStyle),
    color: colors.textTertiary,
    textAlign: "center",
  },
  dayLabelToday: {
    color: colors.accent,
    fontWeight: "700",
  },
  kmLabel: {
    fontSize: 8,
    lineHeight: 11,
    color: colors.textTertiary,
    textAlign: "center",
  },
  kmLabelToday: {
    color: colors.accent,
    fontWeight: "600",
  },
  labelSkeleton: {
    flex: 1,
  },
});
