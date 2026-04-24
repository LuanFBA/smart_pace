import { StyleSheet, View, type ViewStyle } from "react-native";

import { colors, radii, shadows, spacing } from "../theme";

type CardVariant = "elevated" | "flat" | "outlined";

interface CardProps {
  children: React.ReactNode;
  variant?: CardVariant;
  padding?: keyof typeof spacing | "none";
  style?: ViewStyle | ViewStyle[];
}

export function Card({
  children,
  variant = "flat",
  padding = "base",
  style,
}: CardProps) {
  const paddingValue = padding === "none" ? 0 : spacing[padding];

  return (
    <View
      style={[
        styles.base,
        variantStyles[variant],
        { padding: paddingValue },
        style,
      ]}
    >
      {children}
    </View>
  );
}

const styles = StyleSheet.create({
  base: {
    borderRadius: radii.lg,
    backgroundColor: colors.surface,
  },
});

const variantStyles: Record<CardVariant, ViewStyle> = {
  elevated: {
    backgroundColor: colors.surface,
    ...shadows.md,
  },
  flat: {
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border,
  },
  outlined: {
    backgroundColor: "transparent",
    borderWidth: 1,
    borderColor: colors.border,
  },
};
