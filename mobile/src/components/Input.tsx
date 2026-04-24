import type { LucideIcon } from "lucide-react-native";
import { useState } from "react";
import {
  StyleSheet,
  Text,
  TextInput,
  View,
  type KeyboardTypeOptions,
  type TextStyle,
} from "react-native";

import { colors, radii, spacing, typography } from "../theme";

interface InputProps {
  label?: string;
  value: string;
  onChangeText: (text: string) => void;
  secureTextEntry?: boolean;
  keyboardType?: KeyboardTypeOptions;
  autoCapitalize?: "none" | "sentences" | "words" | "characters";
  placeholder?: string;
  error?: string;
  leftIcon?: LucideIcon;
}

export function Input({
  label,
  value,
  onChangeText,
  secureTextEntry,
  keyboardType,
  autoCapitalize = "none",
  placeholder,
  error,
  leftIcon: LeftIcon,
}: InputProps) {
  const [focused, setFocused] = useState(false);
  const hasError = Boolean(error);

  const borderColor = hasError
    ? colors.danger
    : focused
      ? colors.accent
      : colors.borderStrong;

  return (
    <View style={styles.container}>
      {label ? <Text style={styles.label}>{label}</Text> : null}
      <View style={[styles.field, { borderColor }]}>
        {LeftIcon ? (
          <LeftIcon
            color={focused ? colors.accent : colors.textTertiary}
            size={18}
            strokeWidth={2}
          />
        ) : null}
        <TextInput
          style={styles.input}
          value={value}
          onChangeText={onChangeText}
          secureTextEntry={secureTextEntry}
          keyboardType={keyboardType}
          autoCapitalize={autoCapitalize}
          placeholder={placeholder}
          placeholderTextColor={colors.textTertiary}
          onFocus={() => setFocused(true)}
          onBlur={() => setFocused(false)}
        />
      </View>
      {error ? <Text style={styles.error}>{error}</Text> : null}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    marginBottom: spacing.base,
  },
  label: {
    ...(typography.bodySm as TextStyle),
    color: colors.textSecondary,
    marginBottom: spacing.xs,
    fontWeight: "500",
  },
  field: {
    flexDirection: "row",
    alignItems: "center",
    height: 50,
    borderWidth: 1,
    borderRadius: radii.md,
    paddingHorizontal: spacing.md,
    gap: spacing.sm,
    backgroundColor: colors.surface,
  },
  input: {
    flex: 1,
    ...(typography.body as TextStyle),
    color: colors.textPrimary,
    paddingVertical: 0,
  },
  error: {
    ...(typography.caption as TextStyle),
    color: colors.danger,
    marginTop: spacing.xs,
  },
});
