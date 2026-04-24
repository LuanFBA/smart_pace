import { LinearGradient } from "expo-linear-gradient";
import { Pressable, StyleSheet, Text, View, type TextStyle } from "react-native";

import { colors, spacing, typography } from "../../theme";
import { extractInitials, greetingByHour } from "../../utils/format";

interface DashboardHeaderProps {
  displayName: string | null;
  email: string | null;
  subtitle?: string;
  onAvatarPress?: () => void;
}

export function DashboardHeader({
  displayName,
  email,
  subtitle,
  onAvatarPress,
}: DashboardHeaderProps) {
  // Usa apenas o primeiro nome na saudação para ficar mais íntimo
  const firstName = displayName?.split(" ")[0] ?? null;
  const greeting = greetingByHour(new Date().getHours());
  const identitySource = displayName ?? email;

  return (
    <LinearGradient
      colors={[colors.surface, colors.background]}
      start={{ x: 0, y: 0 }}
      end={{ x: 0, y: 1 }}
      style={styles.container}
    >
      <View style={styles.row}>
        <View style={styles.textColumn}>
          <Text style={styles.greeting} numberOfLines={1}>
            {greeting}
            {firstName ? `, ${firstName}` : ""}
          </Text>
          {subtitle ? (
            <Text style={styles.subtitle} numberOfLines={1}>
              {subtitle}
            </Text>
          ) : null}
        </View>

        <Pressable style={styles.avatar} onPress={onAvatarPress}>
          <Text style={styles.avatarText}>{extractInitials(identitySource)}</Text>
        </Pressable>
      </View>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: {
    paddingTop: spacing.xl,
    paddingBottom: spacing.lg,
    paddingHorizontal: spacing.xl,
  },
  row: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    gap: spacing.base,
  },
  textColumn: {
    flex: 1,
    gap: 4,
  },
  greeting: {
    ...(typography.displayMd as TextStyle),
    color: colors.textPrimary,
  },
  subtitle: {
    ...(typography.bodySm as TextStyle),
    color: colors.textSecondary,
  },
  avatar: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: colors.accentSoft,
    alignItems: "center",
    justifyContent: "center",
  },
  avatarText: {
    ...(typography.titleSm as TextStyle),
    color: colors.accent,
    fontWeight: "700",
  },
});
