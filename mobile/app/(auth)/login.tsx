import { ArrowRight, Lock, Mail, Zap } from "lucide-react-native";
import { useState } from "react";
import {
  Keyboard,
  KeyboardAvoidingView,
  Platform,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  View,
  type TextStyle,
} from "react-native";
import { Link } from "expo-router";

import { Button } from "../../src/components/Button";
import { Card } from "../../src/components/Card";
import { Input } from "../../src/components/Input";
import { useAuth } from "../../src/hooks/use-auth";
import { colors, spacing, typography } from "../../src/theme";

export default function LoginScreen() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const { login, isLoading, error } = useAuth();

  const handleLogin = () => {
    Keyboard.dismiss();
    login(email, password);
  };

  return (
    <KeyboardAvoidingView
      style={styles.root}
      behavior={Platform.OS === "ios" ? "padding" : "height"}
    >
      <ScrollView
        contentContainerStyle={styles.content}
        keyboardShouldPersistTaps="handled"
        showsVerticalScrollIndicator={false}
      >
        {/* Logo */}
        <View style={styles.logoBlock}>
          <View style={styles.logoCircle}>
            <Zap color={colors.accent} size={32} strokeWidth={2.5} />
          </View>
          <Text style={styles.appName}>SmartPace</Text>
          <Text style={styles.tagline}>Treine com inteligência</Text>
        </View>

        {/* Formulário */}
        <View style={styles.form}>
          <Input
            label="Email"
            value={email}
            onChangeText={setEmail}
            keyboardType="email-address"
            autoCapitalize="none"
            placeholder="seu@email.com"
            leftIcon={Mail}
          />

          <Input
            label="Senha"
            value={password}
            onChangeText={setPassword}
            secureTextEntry
            placeholder="••••••••"
            leftIcon={Lock}
          />

          {error ? (
            <Card variant="flat" padding="md" style={styles.errorCard}>
              <Text style={styles.errorText}>{error}</Text>
            </Card>
          ) : null}

          <Button
            label="Entrar"
            onPress={handleLogin}
            loading={isLoading}
            fullWidth
            size="lg"
            rightIcon={ArrowRight}
          />
        </View>

        {/* Link para cadastro */}
        <View style={styles.footer}>
          <Text style={styles.footerText}>Não tem conta?</Text>
          <Link href="/(auth)/register" asChild>
            <Pressable style={styles.linkPressable}>
              <Text style={styles.linkText}>Cadastre-se</Text>
              <ArrowRight color={colors.accent} size={14} strokeWidth={2.5} />
            </Pressable>
          </Link>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  root: {
    flex: 1,
    backgroundColor: colors.background,
  },
  content: {
    flexGrow: 1,
    justifyContent: "center",
    paddingHorizontal: spacing.xl,
    paddingVertical: spacing["3xl"],
    gap: spacing["2xl"],
  },
  // --- Logo ---
  logoBlock: {
    alignItems: "center",
    gap: spacing.sm,
  },
  logoCircle: {
    width: 72,
    height: 72,
    borderRadius: 36,
    backgroundColor: colors.accentMuted,
    alignItems: "center",
    justifyContent: "center",
    marginBottom: spacing.sm,
  },
  appName: {
    ...(typography.displayLg as TextStyle),
    color: colors.textPrimary,
  },
  tagline: {
    ...(typography.body as TextStyle),
    color: colors.textSecondary,
  },
  // --- Formulário ---
  form: {
    gap: spacing.sm,
  },
  errorCard: {
    backgroundColor: colors.dangerSoft,
    borderColor: colors.danger,
  },
  errorText: {
    ...(typography.bodySm as TextStyle),
    color: colors.danger,
    textAlign: "center",
  },
  // --- Footer ---
  footer: {
    flexDirection: "row",
    justifyContent: "center",
    alignItems: "center",
    gap: spacing.xs,
  },
  footerText: {
    ...(typography.bodySm as TextStyle),
    color: colors.textSecondary,
  },
  linkPressable: {
    flexDirection: "row",
    alignItems: "center",
    gap: 4,
  },
  linkText: {
    ...(typography.bodySm as TextStyle),
    color: colors.accent,
    fontWeight: "600",
  },
});
