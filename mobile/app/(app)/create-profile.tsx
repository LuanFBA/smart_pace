import { useState } from "react";
import {
  KeyboardAvoidingView,
  Platform,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
  type TextStyle,
} from "react-native";
import { router, Stack } from "expo-router";
import { Activity, Bike } from "lucide-react-native";

import { Button } from "../../src/components/Button";
import { Card } from "../../src/components/Card";
import { useAuthStore } from "../../src/stores/auth-store";
import { createProfile } from "../../src/services/auth-service";
import { ApiError } from "../../src/types/api";
import { colors, radii, spacing, typography } from "../../src/theme";
import type { SportType } from "../../src/types/api";

// Converte DD/MM/YYYY → YYYY-MM-DD para envio à API
function parseDateInput(value: string): string | null {
  const parts = value.split("/");
  if (parts.length !== 3) return null;
  const [day, month, year] = parts;
  if (!day || !month || !year || year.length !== 4) return null;
  const iso = `${year}-${month.padStart(2, "0")}-${day.padStart(2, "0")}`;
  const date = new Date(iso);
  if (isNaN(date.getTime())) return null;
  return iso;
}

// Aplica máscara DD/MM/YYYY ao digitar
function applyDateMask(raw: string): string {
  const digits = raw.replace(/\D/g, "").slice(0, 8);
  if (digits.length <= 2) return digits;
  if (digits.length <= 4) return `${digits.slice(0, 2)}/${digits.slice(2)}`;
  return `${digits.slice(0, 2)}/${digits.slice(2, 4)}/${digits.slice(4)}`;
}

export default function CreateProfileScreen() {
  const setAthleteProfileId = useAuthStore((state) => state.setAthleteProfileId);

  const [sportType, setSportType] = useState<SportType>("running");
  const [dateOfBirth, setDateOfBirth] = useState("");
  const [restingHr, setRestingHr] = useState("");
  const [maxHr, setMaxHr] = useState("");
  const [experienceYears, setExperienceYears] = useState("");
  const [weeklyHours, setWeeklyHours] = useState("");
  const [ftp, setFtp] = useState("");
  const [vo2max, setVo2max] = useState("");

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});

  function validate(): boolean {
    const errors: Record<string, string> = {};

    const isoDate = parseDateInput(dateOfBirth);
    if (!isoDate) errors.dateOfBirth = "Data inválida. Use DD/MM/AAAA";

    const rHr = parseInt(restingHr, 10);
    if (!restingHr || isNaN(rHr) || rHr < 30 || rHr > 120)
      errors.restingHr = "FC de repouso inválida (30–120 bpm)";

    const mHr = parseInt(maxHr, 10);
    if (!maxHr || isNaN(mHr) || mHr < 100 || mHr > 250)
      errors.maxHr = "FC máxima inválida (100–250 bpm)";

    if (rHr >= mHr) errors.maxHr = "FC máxima deve ser maior que FC de repouso";

    const exp = parseInt(experienceYears, 10);
    if (experienceYears && (isNaN(exp) || exp < 0 || exp > 60))
      errors.experienceYears = "Anos de experiência inválido";

    const wh = parseFloat(weeklyHours);
    if (weeklyHours && (isNaN(wh) || wh < 0 || wh > 40))
      errors.weeklyHours = "Meta semanal inválida (0–40h)";

    if (sportType === "cycling" && ftp) {
      const ftpVal = parseInt(ftp, 10);
      if (isNaN(ftpVal) || ftpVal < 50 || ftpVal > 600)
        errors.ftp = "FTP inválido (50–600 W)";
    }

    if (vo2max) {
      const v = parseFloat(vo2max);
      if (isNaN(v) || v < 20 || v > 100)
        errors.vo2max = "VO₂Max inválido (20–100)";
    }

    setFieldErrors(errors);
    return Object.keys(errors).length === 0;
  }

  async function handleSubmit() {
    if (!validate()) return;

    setIsLoading(true);
    setError(null);
    try {
      const profile = await createProfile({
        sport_type: sportType,
        date_of_birth: parseDateInput(dateOfBirth)!,
        resting_heart_rate: parseInt(restingHr, 10),
        maximum_heart_rate: parseInt(maxHr, 10),
        training_experience_years: experienceYears ? parseInt(experienceYears, 10) : 0,
        weekly_target_hours: weeklyHours ? parseFloat(weeklyHours) : 0,
        functional_threshold_power:
          sportType === "cycling" && ftp ? parseInt(ftp, 10) : null,
        current_vo2max: vo2max ? parseFloat(vo2max) : null,
      });

      setAthleteProfileId(profile.id);
      // Volta para o dashboard sem empilhar uma nova instância
      if (router.canGoBack()) {
        router.back();
      } else {
        router.replace("/(app)/dashboard");
      }
    } catch (err) {
      const message =
        err instanceof ApiError ? err.message : "Erro ao criar perfil";
      setError(message);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <>
      <Stack.Screen options={{ title: "Criar perfil de atleta" }} />
      <KeyboardAvoidingView
        style={styles.flex}
        behavior={Platform.OS === "ios" ? "padding" : undefined}
      >
        <ScrollView
          style={styles.root}
          contentContainerStyle={styles.content}
          keyboardShouldPersistTaps="handled"
          showsVerticalScrollIndicator={false}
        >
          {/* Tipo de esporte */}
          <FormSection title="Modalidade">
            <View style={styles.sportRow}>
              <SportButton
                label="Corrida"
                icon={Activity}
                selected={sportType === "running"}
                onPress={() => setSportType("running")}
              />
              <SportButton
                label="Ciclismo"
                icon={Bike}
                selected={sportType === "cycling"}
                onPress={() => setSportType("cycling")}
              />
            </View>
          </FormSection>

          {/* Dados pessoais */}
          <FormSection title="Dados pessoais">
            <FormField
              label="Data de nascimento"
              placeholder="DD/MM/AAAA"
              value={dateOfBirth}
              onChangeText={(t) => setDateOfBirth(applyDateMask(t))}
              keyboardType="numeric"
              error={fieldErrors.dateOfBirth}
            />
          </FormSection>

          {/* Frequência cardíaca */}
          <FormSection title="Frequência cardíaca">
            <FormField
              label="FC em repouso (bpm)"
              placeholder="ex: 55"
              value={restingHr}
              onChangeText={setRestingHr}
              keyboardType="numeric"
              error={fieldErrors.restingHr}
            />
            <FormField
              label="FC máxima (bpm)"
              placeholder="ex: 185"
              value={maxHr}
              onChangeText={setMaxHr}
              keyboardType="numeric"
              error={fieldErrors.maxHr}
            />
          </FormSection>

          {/* Experiência e volume */}
          <FormSection title="Treino">
            <FormField
              label="Anos de experiência"
              placeholder="ex: 2"
              value={experienceYears}
              onChangeText={setExperienceYears}
              keyboardType="numeric"
              error={fieldErrors.experienceYears}
            />
            <FormField
              label="Meta semanal de treino (horas)"
              placeholder="ex: 8"
              value={weeklyHours}
              onChangeText={setWeeklyHours}
              keyboardType="decimal-pad"
              error={fieldErrors.weeklyHours}
            />
          </FormSection>

          {/* Campos opcionais */}
          <FormSection title="Métricas avançadas (opcional)">
            {sportType === "cycling" ? (
              <FormField
                label="FTP — Limiar de potência funcional (W)"
                placeholder="ex: 220"
                value={ftp}
                onChangeText={setFtp}
                keyboardType="numeric"
                error={fieldErrors.ftp}
              />
            ) : null}
            <FormField
              label="VO₂Max (ml/kg/min)"
              placeholder="ex: 52.5"
              value={vo2max}
              onChangeText={setVo2max}
              keyboardType="decimal-pad"
              error={fieldErrors.vo2max}
            />
          </FormSection>

          {/* Erro global */}
          {error ? (
            <Card variant="flat" padding="base" style={styles.errorCard}>
              <Text style={styles.errorText}>{error}</Text>
            </Card>
          ) : null}

          <Button
            label="Criar perfil"
            onPress={handleSubmit}
            loading={isLoading}
            fullWidth
            size="lg"
          />
        </ScrollView>
      </KeyboardAvoidingView>
    </>
  );
}

// --- Componentes internos ---

function FormSection({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <View style={sectionStyles.container}>
      <Text style={sectionStyles.title}>{title}</Text>
      <Card variant="flat" padding="base" style={sectionStyles.card}>
        {children}
      </Card>
    </View>
  );
}

function FormField({
  label,
  placeholder,
  value,
  onChangeText,
  keyboardType,
  error,
}: {
  label: string;
  placeholder?: string;
  value: string;
  onChangeText: (text: string) => void;
  keyboardType?: "numeric" | "decimal-pad";
  error?: string;
}) {
  return (
    <View style={fieldStyles.container}>
      <Text style={fieldStyles.label}>{label}</Text>
      <TextInput
        style={[fieldStyles.input, error ? fieldStyles.inputError : null]}
        value={value}
        onChangeText={onChangeText}
        placeholder={placeholder}
        placeholderTextColor={colors.textTertiary}
        keyboardType={keyboardType ?? "default"}
      />
      {error ? <Text style={fieldStyles.error}>{error}</Text> : null}
    </View>
  );
}

function SportButton({
  label,
  icon: Icon,
  selected,
  onPress,
}: {
  label: string;
  icon: React.ComponentType<{ color: string; size: number; strokeWidth: number }>;
  selected: boolean;
  onPress: () => void;
}) {
  return (
    <Pressable
      style={[sportStyles.button, selected && sportStyles.selected]}
      onPress={onPress}
    >
      <Icon
        color={selected ? colors.accent : colors.textTertiary}
        size={22}
        strokeWidth={2}
      />
      <Text style={[sportStyles.label, selected && sportStyles.labelSelected]}>
        {label}
      </Text>
    </Pressable>
  );
}

// --- Styles ---

const styles = StyleSheet.create({
  flex: { flex: 1 },
  root: {
    flex: 1,
    backgroundColor: colors.background,
  },
  content: {
    paddingHorizontal: spacing.xl,
    paddingTop: spacing.xl,
    paddingBottom: spacing["3xl"],
    gap: spacing["2xl"],
  },
  sportRow: {
    flexDirection: "row",
    gap: spacing.sm,
  },
  errorCard: {
    borderColor: colors.danger,
    backgroundColor: colors.dangerSoft,
  },
  errorText: {
    ...(typography.bodySm as TextStyle),
    color: colors.danger,
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
  card: {
    gap: spacing.base,
  },
});

const fieldStyles = StyleSheet.create({
  container: {
    gap: spacing.xs,
  },
  label: {
    ...(typography.bodySm as TextStyle),
    color: colors.textSecondary,
    fontWeight: "500",
  },
  input: {
    height: 48,
    borderWidth: 1,
    borderColor: colors.borderStrong,
    borderRadius: radii.md,
    paddingHorizontal: spacing.md,
    ...(typography.body as TextStyle),
    color: colors.textPrimary,
    backgroundColor: colors.background,
  },
  inputError: {
    borderColor: colors.danger,
  },
  error: {
    ...(typography.caption as TextStyle),
    color: colors.danger,
  },
});

const sportStyles = StyleSheet.create({
  button: {
    flex: 1,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    gap: spacing.sm,
    height: 52,
    borderWidth: 1.5,
    borderColor: colors.border,
    borderRadius: radii.md,
    backgroundColor: colors.background,
  },
  selected: {
    borderColor: colors.accent,
    backgroundColor: colors.accentSoft,
  },
  label: {
    ...(typography.bodyStrong as TextStyle),
    color: colors.textSecondary,
  },
  labelSelected: {
    color: colors.accent,
  },
});
