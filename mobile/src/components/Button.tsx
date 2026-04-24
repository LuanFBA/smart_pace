import type { LucideIcon } from "lucide-react-native";
import {
  ActivityIndicator,
  Pressable,
  StyleSheet,
  Text,
  View,
  type PressableProps,
  type TextStyle,
  type ViewStyle,
} from "react-native";
import Animated, {
  useAnimatedStyle,
  useSharedValue,
  withTiming,
} from "react-native-reanimated";

import { colors, radii, spacing, typography } from "../theme";

type ButtonVariant = "primary" | "secondary" | "ghost" | "danger";
type ButtonSize = "md" | "lg";

interface ButtonProps {
  label: string;
  onPress: PressableProps["onPress"];
  loading?: boolean;
  disabled?: boolean;
  variant?: ButtonVariant;
  size?: ButtonSize;
  fullWidth?: boolean;
  leftIcon?: LucideIcon;
  rightIcon?: LucideIcon;
}

const AnimatedPressable = Animated.createAnimatedComponent(Pressable);

export function Button({
  label,
  onPress,
  loading = false,
  disabled = false,
  variant = "primary",
  size = "md",
  fullWidth = false,
  leftIcon: LeftIcon,
  rightIcon: RightIcon,
}: ButtonProps) {
  const isDisabled = loading || disabled;
  const scale = useSharedValue(1);

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ scale: scale.value }],
  }));

  const handlePressIn = () => {
    scale.value = withTiming(0.97, { duration: 90 });
  };
  const handlePressOut = () => {
    scale.value = withTiming(1, { duration: 140 });
  };

  const variantStyle = variantStyles[variant];
  const labelColor = variantLabelColors[variant];
  const sizeStyle = size === "lg" ? sizeStyles.lg : sizeStyles.md;
  const iconColor = labelColor;
  const iconSize = size === "lg" ? 20 : 18;

  return (
    <AnimatedPressable
      onPress={onPress}
      onPressIn={handlePressIn}
      onPressOut={handlePressOut}
      disabled={isDisabled}
      style={[
        styles.base,
        sizeStyle,
        variantStyle,
        fullWidth && styles.fullWidth,
        isDisabled && styles.disabled,
        animatedStyle,
      ]}
    >
      {loading ? (
        <ActivityIndicator color={labelColor} size="small" />
      ) : (
        <View style={styles.content}>
          {LeftIcon ? (
            <LeftIcon color={iconColor} size={iconSize} strokeWidth={2} />
          ) : null}
          <Text style={[styles.label, { color: labelColor }]}>{label}</Text>
          {RightIcon ? (
            <RightIcon color={iconColor} size={iconSize} strokeWidth={2} />
          ) : null}
        </View>
      )}
    </AnimatedPressable>
  );
}

const styles = StyleSheet.create({
  base: {
    borderRadius: radii.md,
    alignItems: "center",
    justifyContent: "center",
  },
  content: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.sm,
  },
  label: {
    ...(typography.titleSm as TextStyle),
  },
  fullWidth: {
    alignSelf: "stretch",
  },
  disabled: {
    opacity: 0.5,
  },
});

const sizeStyles: Record<ButtonSize, ViewStyle> = {
  md: {
    height: 48,
    paddingHorizontal: spacing.lg,
  },
  lg: {
    height: 54,
    paddingHorizontal: spacing.xl,
  },
};

const variantStyles: Record<ButtonVariant, ViewStyle> = {
  primary: {
    backgroundColor: colors.accent,
  },
  secondary: {
    backgroundColor: colors.gray100,
  },
  ghost: {
    backgroundColor: "transparent",
  },
  danger: {
    backgroundColor: colors.danger,
  },
};

const variantLabelColors: Record<ButtonVariant, string> = {
  primary: colors.textInverse,
  secondary: colors.textPrimary,
  ghost: colors.accent,
  danger: colors.textInverse,
};
