import { CalendarDays, UserPlus } from "lucide-react-native";
import { StyleSheet, Text, View, type TextStyle } from "react-native";

const MONTHS_SHORT = [
  "jan", "fev", "mar", "abr", "mai", "jun",
  "jul", "ago", "set", "out", "nov", "dez",
];

// Retorna "Hoje · 14 abr"
function todayLabel(): string {
  const now = new Date();
  return `Hoje · ${now.getDate()} ${MONTHS_SHORT[now.getMonth()]}`;
}

import { Button } from "../../components/Button";
import { Card } from "../../components/Card";
import { Skeleton } from "../../components/Skeleton";
import { colors, radii, spacing, typography } from "../../theme";
import type { SessionType } from "../../types/api";
import {
  FALLBACK_SESSION_ICON,
  SESSION_TYPE_DESCRIPTIONS,
  SESSION_TYPE_ICONS,
  SESSION_TYPE_LABELS,
} from "../../utils/session-labels";

interface NextWorkoutCardProps {
  sessionType: SessionType | null;
  isLoading?: boolean;
  hasProfile?: boolean;
  error?: string | null;
  onRetry?: () => void;
  onCreateProfile?: () => void;
}

export function NextWorkoutCard({
  sessionType,
  isLoading = false,
  hasProfile = true,
  error = null,
  onRetry,
  onCreateProfile,
}: NextWorkoutCardProps) {
  if (!hasProfile) {
    return (
      <Card variant="flat" padding="lg" style={styles.card}>
        <View style={styles.emptyState}>
          <UserPlus color={colors.textTertiary} size={32} strokeWidth={1.5} />
          <Text style={styles.emptyTitle}>Sem perfil de atleta</Text>
          <Text style={styles.emptySubtitle}>
            Crie seu perfil para receber sugestões personalizadas de treino
          </Text>
          {onCreateProfile ? (
            <Button
              label="Criar perfil"
              variant="secondary"
              onPress={onCreateProfile}
            />
          ) : null}
        </View>
      </Card>
    );
  }

  if (isLoading) {
    return (
      <Card variant="elevated" padding="lg" style={styles.card}>
        <View style={styles.loadingContent}>
          <Skeleton width={44} height={44} borderRadius={22} />
          <View style={{ flex: 1, gap: 8 }}>
            <Skeleton height={18} width="60%" />
            <Skeleton height={13} width="85%" />
          </View>
        </View>
      </Card>
    );
  }

  if (error) {
    return (
      <Card variant="flat" padding="lg" style={styles.card}>
        <Text style={styles.errorText}>{error}</Text>
        {onRetry ? (
          <Button label="Tentar novamente" variant="ghost" onPress={onRetry} />
        ) : null}
      </Card>
    );
  }

  if (!sessionType) return null;

  const IconComponent = SESSION_TYPE_ICONS[sessionType] ?? FALLBACK_SESSION_ICON;
  const label = SESSION_TYPE_LABELS[sessionType];
  const description = SESSION_TYPE_DESCRIPTIONS[sessionType];

  return (
    <Card variant="elevated" padding="lg" style={styles.card}>
      <View style={styles.cardContent}>
        <View style={styles.iconContainer}>
          <IconComponent color={colors.accent} size={24} strokeWidth={2} />
        </View>
        <View style={styles.textContent}>
          <Text style={styles.sessionLabel}>{label}</Text>
          <Text style={styles.sessionDescription} numberOfLines={2}>
            {description}
          </Text>
        </View>
      </View>

      <View style={styles.meta}>
        <CalendarDays color={colors.accent} size={13} strokeWidth={2} />
        <Text style={styles.metaText}>{todayLabel()}</Text>
      </View>
    </Card>
  );
}

const styles = StyleSheet.create({
  card: {
    gap: spacing.base,
  },
  // --- Estado: sem perfil ---
  emptyState: {
    alignItems: "center",
    gap: spacing.sm,
    paddingVertical: spacing.md,
  },
  emptyTitle: {
    ...(typography.titleSm as TextStyle),
    color: colors.textPrimary,
    marginTop: spacing.xs,
  },
  emptySubtitle: {
    ...(typography.bodySm as TextStyle),
    color: colors.textSecondary,
    textAlign: "center",
  },
  // --- Estado: carregando ---
  loadingContent: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.md,
  },
  // --- Estado: erro ---
  errorText: {
    ...(typography.bodySm as TextStyle),
    color: colors.danger,
    textAlign: "center",
  },
  // --- Conteúdo normal ---
  cardContent: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.md,
  },
  iconContainer: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: colors.accentMuted,
    alignItems: "center",
    justifyContent: "center",
  },
  textContent: {
    flex: 1,
    gap: 4,
  },
  sessionLabel: {
    ...(typography.titleMd as TextStyle),
    color: colors.textPrimary,
  },
  sessionDescription: {
    ...(typography.bodySm as TextStyle),
    color: colors.textSecondary,
  },
  meta: {
    flexDirection: "row",
    alignItems: "center",
    alignSelf: "flex-start",
    gap: spacing.xs,
    paddingVertical: 4,
    paddingHorizontal: spacing.sm,
    borderRadius: radii.pill,
    backgroundColor: colors.accentSoft,
  },
  metaText: {
    ...(typography.caption as TextStyle),
    color: colors.accent,
    fontWeight: "600",
  },
});
