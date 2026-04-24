import { Activity, Bike, Heart, LogOut, RefreshCw, UserX } from "lucide-react-native";
import {
  ScrollView,
  StyleSheet,
  Text,
  View,
  type TextStyle,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";

import { useAuth } from "../../../src/hooks/use-auth";

import { Button } from "../../../src/components/Button";
import { Card } from "../../../src/components/Card";
import { Skeleton } from "../../../src/components/Skeleton";
import { useProfile } from "../../../src/hooks/use-profile";
import { useAuthStore } from "../../../src/stores/auth-store";
import { colors, radii, spacing, typography } from "../../../src/theme";
import { readIdentityFromToken } from "../../../src/utils/auth-claims";
import { extractInitials, formatDate } from "../../../src/utils/format";
import type { HeartRateZone } from "../../../src/types/api";

// Cores fixas para as 5 zonas de FC (sequência fisiológica)
const ZONE_COLORS = ["#60a5fa", "#34d399", "#fbbf24", "#f97316", "#ef4444"];

// Calcula idade a partir da data ISO de nascimento
// Parseia a string diretamente para evitar desvio de dia por timezone
function calcAge(dateOfBirth: string): number {
  const [y, m, d] = dateOfBirth.split("T")[0].split("-").map(Number);
  const today = new Date();
  let age = today.getFullYear() - y;
  const monthDiff = today.getMonth() + 1 - m;
  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < d)) {
    age--;
  }
  return age;
}

export default function ProfileScreen() {
  const { logout } = useAuth();
  const accessToken = useAuthStore((state) => state.accessToken);
  const storedFullName = useAuthStore((state) => state.fullName);
  const { email } = readIdentityFromToken(accessToken);
  const { profile, isLoading, error, refetch } = useProfile();

  // Nome: do store (persistido no login) ou do perfil carregado — o que vier primeiro
  const displayName = storedFullName ?? profile?.user_full_name ?? null;
  const identitySource = displayName ?? email;
  const initials = extractInitials(identitySource);

  return (
    <SafeAreaView style={styles.root} edges={["top"]}>
      <ScrollView
        contentContainerStyle={styles.content}
        showsVerticalScrollIndicator={false}
      >
        <Text style={styles.screenTitle}>Perfil</Text>
        {/* Cabeçalho de identidade */}
        <View style={styles.identityBlock}>
          <View style={styles.avatar}>
            <Text style={styles.avatarText}>{initials}</Text>
          </View>
          {isLoading && !displayName ? (
            <Skeleton width={160} height={26} borderRadius={radii.sm} />
          ) : displayName ? (
            <Text style={styles.name}>{displayName}</Text>
          ) : null}
          {email ? (
            <Text style={styles.email}>{email}</Text>
          ) : null}
        </View>

        {/* Estado de erro */}
        {error ? (
          <Card variant="flat" padding="base" style={styles.errorCard}>
            <Text style={styles.errorText}>{error}</Text>
            <Button
              label="Tentar novamente"
              variant="ghost"
              onPress={refetch}
              leftIcon={RefreshCw}
            />
          </Card>
        ) : null}

        {/* Estado sem perfil */}
        {!isLoading && !error && profile === null ? (
          <Card variant="flat" padding="base" style={styles.emptyCard}>
            <UserX color={colors.textTertiary} size={32} strokeWidth={1.5} />
            <Text style={styles.emptyTitle}>Sem perfil de atleta</Text>
            <Text style={styles.emptyText}>
              Você ainda não criou seu perfil de atleta. Entre em contato com o
              suporte ou use o fluxo de cadastro para configurar seus dados.
            </Text>
          </Card>
        ) : null}

        {/* Skeleton de loading */}
        {isLoading ? (
          <View style={styles.skeletonBlock}>
            <Skeleton height={20} width="60%" />
            <Skeleton height={96} />
            <Skeleton height={20} width="50%" />
            <Skeleton height={120} />
            <Skeleton height={20} width="55%" />
            <Skeleton height={160} />
          </View>
        ) : null}

        {/* Conteúdo do perfil */}
        {!isLoading && !error && profile !== null ? (
          <>
            {/* Seção: dados do atleta */}
            <Section title="Dados do atleta">
              <View style={styles.statsGrid}>
                <StatCard
                  icon={profile.sport_type === "cycling" ? Bike : Activity}
                  iconColor={colors.accent}
                  label="Esporte"
                  value={profile.sport_type === "cycling" ? "Ciclismo" : "Corrida"}
                />
                <StatCard
                  icon={null}
                  label="Idade"
                  value={`${calcAge(profile.date_of_birth)} anos`}
                />
                <StatCard
                  icon={null}
                  label="Experiência"
                  value={`${profile.training_experience_years} ano${profile.training_experience_years !== 1 ? "s" : ""}`}
                />
                <StatCard
                  icon={null}
                  label="Meta semanal"
                  value={`${profile.weekly_target_hours}h`}
                />
              </View>
            </Section>

            {/* Seção: métricas de aptidão */}
            <Section title="Métricas de aptidão">
              <Card variant="flat" padding="base">
                <MetricRow
                  label="FC em repouso"
                  value={`${profile.resting_heart_rate} bpm`}
                />
                <Divider />
                <MetricRow
                  label="FC máxima"
                  value={`${profile.maximum_heart_rate} bpm`}
                />
                {profile.current_vo2max !== null ? (
                  <>
                    <Divider />
                    <MetricRow
                      label="VO₂Max"
                      value={`${profile.current_vo2max.toFixed(1)} ml/kg/min`}
                    />
                  </>
                ) : null}
                {profile.functional_threshold_power !== null ? (
                  <>
                    <Divider />
                    <MetricRow
                      label="FTP"
                      value={`${profile.functional_threshold_power} W`}
                    />
                  </>
                ) : null}
              </Card>
            </Section>

            {/* Seção: zonas de FC */}
            {profile.heart_rate_zones.length > 0 ? (
              <Section title="Zonas de frequência cardíaca">
                <Card variant="flat" padding="base">
                  {profile.heart_rate_zones.map((zone, index) => (
                    <View key={zone.name}>
                      <HrZoneRow
                        zone={zone}
                        color={ZONE_COLORS[index] ?? colors.accent}
                      />
                      {index < profile.heart_rate_zones.length - 1 ? (
                        <Divider />
                      ) : null}
                    </View>
                  ))}
                </Card>
              </Section>
            ) : null}

            {/* Linha discreta com data de nascimento */}
            <Text style={styles.birthDate}>
              Data de nascimento: {formatDate(profile.date_of_birth)}
            </Text>
          </>
        ) : null}

        {/* Logout */}
        <Button
          label="Sair da conta"
          variant="danger"
          onPress={logout}
          leftIcon={LogOut}
          fullWidth
        />
      </ScrollView>
    </SafeAreaView>
  );
}

// --- Componentes internos ---

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

function StatCard({
  icon: Icon,
  iconColor,
  label,
  value,
}: {
  icon: React.ComponentType<{ color: string; size: number; strokeWidth: number }> | null;
  iconColor?: string;
  label: string;
  value: string;
}) {
  return (
    <Card variant="flat" padding="base" style={statCardStyles.card}>
      {Icon ? (
        <Icon color={iconColor ?? colors.accent} size={18} strokeWidth={2} />
      ) : (
        <View style={statCardStyles.iconPlaceholder} />
      )}
      <Text style={statCardStyles.value} numberOfLines={1}>{value}</Text>
      <Text style={statCardStyles.label} numberOfLines={1}>{label}</Text>
    </Card>
  );
}

function MetricRow({ label, value }: { label: string; value: string }) {
  return (
    <View style={metricRowStyles.row}>
      <Text style={metricRowStyles.label}>{label}</Text>
      <Text style={metricRowStyles.value}>{value}</Text>
    </View>
  );
}

function HrZoneRow({ zone, color }: { zone: HeartRateZone; color: string }) {
  return (
    <View style={hrZoneStyles.row}>
      <View style={[hrZoneStyles.dot, { backgroundColor: color }]} />
      <Text style={hrZoneStyles.name}>{zone.name}</Text>
      <Text style={hrZoneStyles.range}>
        {zone.min_bpm}–{zone.max_bpm} bpm
      </Text>
    </View>
  );
}

function Divider() {
  return <View style={styles.divider} />;
}

// --- Styles ---

const styles = StyleSheet.create({
  root: {
    flex: 1,
    backgroundColor: colors.background,
  },
  content: {
    paddingHorizontal: spacing.xl,
    paddingTop: spacing.lg,
    paddingBottom: spacing["3xl"],
    gap: spacing["2xl"],
  },
  screenTitle: {
    ...(typography.titleLg as TextStyle),
    color: colors.textPrimary,
  },
  // --- Identidade ---
  identityBlock: {
    alignItems: "center",
    gap: spacing.sm,
  },
  avatar: {
    width: 72,
    height: 72,
    borderRadius: 36,
    backgroundColor: colors.accentSoft,
    alignItems: "center",
    justifyContent: "center",
    marginBottom: spacing.xs,
  },
  avatarText: {
    ...(typography.titleLg as TextStyle),
    color: colors.accent,
    fontWeight: "700",
  },
  name: {
    ...(typography.titleLg as TextStyle),
    color: colors.textPrimary,
    textAlign: "center",
  },
  email: {
    ...(typography.bodySm as TextStyle),
    color: colors.textSecondary,
    textAlign: "center",
  },
  // --- Estados ---
  errorCard: {
    borderColor: colors.danger,
    backgroundColor: colors.dangerSoft,
    gap: spacing.sm,
    alignItems: "center",
  },
  errorText: {
    ...(typography.bodySm as TextStyle),
    color: colors.danger,
    textAlign: "center",
  },
  emptyCard: {
    alignItems: "center",
    gap: spacing.sm,
  },
  emptyTitle: {
    ...(typography.titleSm as TextStyle),
    color: colors.textPrimary,
    textAlign: "center",
  },
  emptyText: {
    ...(typography.bodySm as TextStyle),
    color: colors.textSecondary,
    textAlign: "center",
    lineHeight: 20,
  },
  skeletonBlock: {
    gap: spacing.base,
  },
  // --- Utilitários ---
  divider: {
    height: 1,
    backgroundColor: colors.border,
    marginVertical: spacing.sm,
  },
  statsGrid: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: spacing.sm,
  },
  birthDate: {
    ...(typography.caption as TextStyle),
    color: colors.textTertiary,
    textAlign: "center",
  },
});

const sectionStyles = StyleSheet.create({
  container: {
    gap: spacing.md,
  },
  title: {
    ...(typography.titleSm as TextStyle),
    color: colors.textPrimary,
  },
});

const statCardStyles = StyleSheet.create({
  card: {
    flex: 1,
    minWidth: "45%",
    gap: spacing.xs,
  },
  iconPlaceholder: {
    width: 18,
    height: 18,
  },
  value: {
    ...(typography.titleSm as TextStyle),
    color: colors.textPrimary,
  },
  label: {
    ...(typography.caption as TextStyle),
    color: colors.textSecondary,
  },
});

const metricRowStyles = StyleSheet.create({
  row: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingVertical: spacing.xs,
  },
  label: {
    ...(typography.body as TextStyle),
    color: colors.textSecondary,
  },
  value: {
    ...(typography.bodyStrong as TextStyle),
    color: colors.textPrimary,
  },
});

const hrZoneStyles = StyleSheet.create({
  row: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.sm,
    paddingVertical: spacing.xs,
  },
  dot: {
    width: 10,
    height: 10,
    borderRadius: 5,
  },
  name: {
    ...(typography.body as TextStyle),
    color: colors.textSecondary,
    flex: 1,
  },
  range: {
    ...(typography.bodyStrong as TextStyle),
    color: colors.textPrimary,
  },
});
