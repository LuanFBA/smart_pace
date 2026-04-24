import { useState } from "react";
import {
  KeyboardAvoidingView,
  Modal,
  Platform,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
  type TextStyle,
  type ViewStyle,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { router } from "expo-router";
import DateTimePicker, {
  type DateTimePickerEvent,
} from "@react-native-community/datetimepicker";
import { CalendarDays } from "lucide-react-native";

import { Button } from "../../../src/components/Button";
import { Card } from "../../../src/components/Card";
import { useAuthStore } from "../../../src/stores/auth-store";
import { scheduleSession, logWorkout } from "../../../src/services/workout-service";
import { ApiError } from "../../../src/types/api";
import { colors, radii, shadows, spacing, typography } from "../../../src/theme";
import {
  SESSION_TYPE_LABELS,
  SESSION_TYPE_ICONS,
  FALLBACK_SESSION_ICON,
} from "../../../src/utils/session-labels";
import type { SessionType } from "../../../src/types/api";

// Grupos de modalidade com rótulo visual
const RUNNING_TYPES: SessionType[] = ["easy_run", "tempo", "interval", "long_run", "recovery"];
const CYCLING_TYPES: SessionType[] = ["cycling_endurance", "cycling_interval"];

// --- Helpers ---

const pad = (n: number) => String(n).padStart(2, "0");

// Date → YYYY-MM-DD para o backend
function dateToISO(d: Date): string {
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
}

// Date → DD/MM/YYYY para exibição
function dateToDisplay(d: Date): string {
  return `${pad(d.getDate())}/${pad(d.getMonth() + 1)}/${d.getFullYear()}`;
}

function applyTimeMask(raw: string): string {
  const digits = raw.replace(/\D/g, "").slice(0, 4);
  if (digits.length <= 2) return digits;
  return `${digits.slice(0, 2)}:${digits.slice(2)}`;
}

function timeToSeconds(hhmm: string): number | null {
  const [h, m] = hhmm.split(":").map(Number);
  if (isNaN(h) || isNaN(m) || m >= 60) return null;
  return h * 3600 + m * 60;
}

// Constrói datetime ISO local combinando data YYYY-MM-DD + hora HH:MM
function buildDatetime(isoDate: string, timeHHMM: string): string {
  const [h, m] = timeHHMM.split(":").map(Number);
  const d = new Date(`${isoDate}T00:00:00`);
  d.setHours(h, m, 0, 0);
  return (
    `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}` +
    `T${pad(d.getHours())}:${pad(d.getMinutes())}:00`
  );
}

export default function LogWorkoutScreen() {
  const athleteProfileId = useAuthStore((state) => state.athleteProfileId);

  const [sessionType, setSessionType] = useState<SessionType>("easy_run");
  const [workoutDate, setWorkoutDate] = useState<Date>(new Date());
  const [showDatePicker, setShowDatePicker] = useState(false);
  // tempDate guarda a seleção no iOS antes de confirmar
  const [tempDate, setTempDate] = useState<Date>(new Date());

  const [startTime, setStartTime] = useState("");
  const [duration, setDuration] = useState("");
  const [distanceKm, setDistanceKm] = useState("");
  const [avgHr, setAvgHr] = useState("");
  const [maxHr, setMaxHr] = useState("");
  const [rpe, setRpe] = useState<number | null>(null);
  const [notes, setNotes] = useState("");

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});

  // Callbacks do DateTimePicker
  function onAndroidChange(_: DateTimePickerEvent, selected?: Date) {
    setShowDatePicker(false);
    if (selected) setWorkoutDate(selected);
  }

  function onIOSChange(_: DateTimePickerEvent, selected?: Date) {
    if (selected) setTempDate(selected);
  }

  function confirmIOSDate() {
    setWorkoutDate(tempDate);
    setShowDatePicker(false);
  }

  function cancelIOSDate() {
    setTempDate(workoutDate);
    setShowDatePicker(false);
  }

  function validate(): boolean {
    const errors: Record<string, string> = {};

    if (!startTime || startTime.length < 5)
      errors.startTime = "Informe o horário de início (HH:MM)";

    const durationSecs = timeToSeconds(duration);
    if (!duration || durationSecs === null || durationSecs <= 0)
      errors.duration = "Duração inválida (HH:MM)";

    const distMeters = parseFloat(distanceKm) * 1000;
    if (!distanceKm || isNaN(distMeters) || distMeters <= 0)
      errors.distanceKm = "Distância inválida";

    if (avgHr) {
      const v = parseInt(avgHr, 10);
      if (isNaN(v) || v < 30 || v > 250)
        errors.avgHr = "FC média inválida (30–250 bpm)";
    }
    if (maxHr) {
      const v = parseInt(maxHr, 10);
      if (isNaN(v) || v < 30 || v > 250)
        errors.maxHr = "FC máxima inválida (30–250 bpm)";
    }

    setFieldErrors(errors);
    return Object.keys(errors).length === 0;
  }

  async function handleSubmit() {
    if (!athleteProfileId) return;
    if (!validate()) return;

    setIsLoading(true);
    setError(null);
    try {
      const isoDate = dateToISO(workoutDate);

      const session = await scheduleSession({
        athlete_profile_id: athleteProfileId,
        scheduled_date: isoDate,
        session_type: sessionType,
      });

      const durationSecs = timeToSeconds(duration)!;
      const startedAt = buildDatetime(isoDate, startTime);

      const finishedAtDate = new Date(startedAt);
      finishedAtDate.setSeconds(finishedAtDate.getSeconds() + durationSecs);
      const finishedAt =
        `${finishedAtDate.getFullYear()}-${pad(finishedAtDate.getMonth() + 1)}-${pad(finishedAtDate.getDate())}` +
        `T${pad(finishedAtDate.getHours())}:${pad(finishedAtDate.getMinutes())}:${pad(finishedAtDate.getSeconds())}`;

      await logWorkout({
        workout_session_id: session.id,
        athlete_profile_id: athleteProfileId,
        started_at: startedAt,
        finished_at: finishedAt,
        actual_distance_meters: Math.round(parseFloat(distanceKm) * 1000),
        actual_duration_seconds: durationSecs,
        average_heart_rate: avgHr ? parseInt(avgHr, 10) : null,
        maximum_heart_rate: maxHr ? parseInt(maxHr, 10) : null,
        perceived_exertion: rpe,
        notes: notes.trim() || null,
      });

      // Após salvar, volta para a aba inicial, que recarrega via useFocusEffect
      router.navigate("/(app)/dashboard");
    } catch (err) {
      const message =
        err instanceof ApiError ? err.message : "Erro ao registrar treino";
      setError(message);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <SafeAreaView style={styles.flex}>
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
          {/* Tipo de sessão — separado por modalidade */}
          <FormSection title="Tipo de treino">
            <SportGroup label="Corrida" types={RUNNING_TYPES} selected={sessionType} onSelect={setSessionType} />
            <View style={styles.sportDivider} />
            <SportGroup label="Ciclismo" types={CYCLING_TYPES} selected={sessionType} onSelect={setSessionType} />
          </FormSection>

          {/* Dados do treino */}
          <FormSection title="Dados do treino">
            {/* Campo de data com calendário */}
            <View style={fieldStyles.container}>
              <Text style={fieldStyles.label}>Data</Text>
              <Pressable
                style={styles.dateField}
                onPress={() => {
                  setTempDate(workoutDate);
                  setShowDatePicker(true);
                }}
              >
                <Text style={styles.dateText}>{dateToDisplay(workoutDate)}</Text>
                <CalendarDays color={colors.accent} size={18} strokeWidth={2} />
              </Pressable>
            </View>

            {/* Android: picker renderizado diretamente como dialog nativo */}
            {Platform.OS === "android" && showDatePicker && (
              <DateTimePicker
                value={workoutDate}
                mode="date"
                display="calendar"
                maximumDate={new Date()}
                onChange={onAndroidChange}
              />
            )}

            <View style={styles.row}>
              <View style={styles.rowField}>
                <FormField
                  label="Início"
                  placeholder="HH:MM"
                  value={startTime}
                  onChangeText={(t) => setStartTime(applyTimeMask(t))}
                  keyboardType="numeric"
                  error={fieldErrors.startTime}
                />
              </View>
              <View style={styles.rowField}>
                <FormField
                  label="Duração"
                  placeholder="HH:MM"
                  value={duration}
                  onChangeText={(t) => setDuration(applyTimeMask(t))}
                  keyboardType="numeric"
                  error={fieldErrors.duration}
                />
              </View>
            </View>
            <FormField
              label="Distância (km)"
              placeholder="ex: 10.5"
              value={distanceKm}
              onChangeText={setDistanceKm}
              keyboardType="decimal-pad"
              error={fieldErrors.distanceKm}
            />
          </FormSection>

          {/* Métricas opcionais */}
          <FormSection title="Métricas (opcional)">
            <View style={styles.row}>
              <View style={styles.rowField}>
                <FormField
                  label="FC média (bpm)"
                  placeholder="ex: 148"
                  value={avgHr}
                  onChangeText={setAvgHr}
                  keyboardType="numeric"
                  error={fieldErrors.avgHr}
                />
              </View>
              <View style={styles.rowField}>
                <FormField
                  label="FC máxima (bpm)"
                  placeholder="ex: 172"
                  value={maxHr}
                  onChangeText={setMaxHr}
                  keyboardType="numeric"
                  error={fieldErrors.maxHr}
                />
              </View>
            </View>

            <View>
              <Text style={fieldStyles.label}>Esforço percebido (RPE)</Text>
              <View style={styles.rpeRow}>
                {Array.from({ length: 10 }, (_, i) => i + 1).map((n) => (
                  <Pressable
                    key={n}
                    style={[styles.rpeChip, rpe === n && styles.rpeChipSelected]}
                    onPress={() => setRpe(rpe === n ? null : n)}
                  >
                    <Text style={[styles.rpeLabel, rpe === n && styles.rpeLabelSelected]}>
                      {n}
                    </Text>
                  </Pressable>
                ))}
              </View>
            </View>

            <View>
              <Text style={fieldStyles.label}>Notas</Text>
              <TextInput
                style={[fieldStyles.input, styles.notesInput]}
                value={notes}
                onChangeText={setNotes}
                placeholder="Como foi o treino?"
                placeholderTextColor={colors.textTertiary}
                multiline
                numberOfLines={3}
                textAlignVertical="top"
              />
            </View>
          </FormSection>

          {error ? (
            <Card variant="flat" padding="base" style={styles.errorCard}>
              <Text style={styles.errorText}>{error}</Text>
            </Card>
          ) : null}

          <Button
            label="Salvar treino"
            onPress={handleSubmit}
            loading={isLoading}
            fullWidth
            size="lg"
          />
        </ScrollView>
      </KeyboardAvoidingView>

      {/* iOS: modal com calendário inline + botões de confirmação */}
      {Platform.OS === "ios" && (
        <Modal
          visible={showDatePicker}
          transparent
          animationType="slide"
          onRequestClose={cancelIOSDate}
        >
          <Pressable style={styles.modalOverlay} onPress={cancelIOSDate} />
          <View style={[styles.modalSheet, shadows.lg]}>
            <View style={styles.modalHeader}>
              <Pressable onPress={cancelIOSDate}>
                <Text style={styles.modalCancel}>Cancelar</Text>
              </Pressable>
              <Text style={styles.modalTitle}>Selecionar data</Text>
              <Pressable onPress={confirmIOSDate}>
                <Text style={styles.modalConfirm}>Confirmar</Text>
              </Pressable>
            </View>
            <DateTimePicker
              value={tempDate}
              mode="date"
              display="inline"
              maximumDate={new Date()}
              onChange={onIOSChange}
              locale="pt-BR"
              themeVariant="light"
              style={styles.iosPicker}
            />
          </View>
        </Modal>
      )}
    </SafeAreaView>
  );
}

// --- Componentes internos ---

function SportGroup({
  label,
  types,
  selected,
  onSelect,
}: {
  label: string;
  types: SessionType[];
  selected: SessionType;
  onSelect: (t: SessionType) => void;
}) {
  return (
    <View style={sportGroupStyles.container}>
      <Text style={sportGroupStyles.label}>{label}</Text>
      <View style={sportGroupStyles.chips}>
        {types.map((type) => {
          const Icon = SESSION_TYPE_ICONS[type] ?? FALLBACK_SESSION_ICON;
          const isSelected = selected === type;
          return (
            <Pressable
              key={type}
              style={[styles.sessionChip, isSelected && styles.sessionChipSelected]}
              onPress={() => onSelect(type)}
            >
              <Icon
                color={isSelected ? colors.accent : colors.textTertiary}
                size={14}
                strokeWidth={2}
              />
              <Text style={[styles.sessionChipLabel, isSelected && styles.sessionChipLabelSelected]}>
                {SESSION_TYPE_LABELS[type]}
              </Text>
            </Pressable>
          );
        })}
      </View>
    </View>
  );
}

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
  // --- Tipo de treino ---
  sportDivider: {
    height: 1,
    backgroundColor: colors.border,
  },
  sessionChip: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.xs,
    paddingVertical: spacing.xs,
    paddingHorizontal: spacing.sm,
    borderRadius: radii.pill,
    borderWidth: 1.5,
    borderColor: colors.border,
    backgroundColor: colors.background,
  },
  sessionChipSelected: {
    borderColor: colors.accent,
    backgroundColor: colors.accentSoft,
  },
  sessionChipLabel: {
    ...(typography.caption as TextStyle),
    color: colors.textSecondary,
    fontWeight: "600",
  },
  sessionChipLabelSelected: {
    color: colors.accent,
  },
  // --- Campo de data ---
  dateField: {
    height: 48,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    borderWidth: 1,
    borderColor: colors.borderStrong,
    borderRadius: radii.md,
    paddingHorizontal: spacing.md,
    backgroundColor: colors.background,
  },
  dateText: {
    ...(typography.body as TextStyle),
    color: colors.textPrimary,
  },
  // --- Modal iOS ---
  modalOverlay: {
    flex: 1,
    backgroundColor: "rgba(0,0,0,0.35)",
  },
  modalSheet: {
    backgroundColor: colors.surface,
    borderTopLeftRadius: radii.xl,
    borderTopRightRadius: radii.xl,
    paddingBottom: spacing["3xl"],
  } as ViewStyle,
  modalHeader: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    paddingHorizontal: spacing.xl,
    paddingVertical: spacing.base,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  modalTitle: {
    ...(typography.titleSm as TextStyle),
    color: colors.textPrimary,
  },
  modalCancel: {
    ...(typography.body as TextStyle),
    color: colors.textSecondary,
  },
  modalConfirm: {
    ...(typography.bodyStrong as TextStyle),
    color: colors.accent,
  },
  iosPicker: {
    alignSelf: "center",
  },
  // --- Outros ---
  row: {
    flexDirection: "row",
    gap: spacing.sm,
  },
  rowField: {
    flex: 1,
  },
  rpeRow: {
    flexDirection: "row",
    gap: spacing.xs,
    flexWrap: "wrap",
    marginTop: spacing.xs,
  },
  rpeChip: {
    width: 36,
    height: 36,
    borderRadius: radii.md,
    borderWidth: 1.5,
    borderColor: colors.border,
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: colors.background,
  },
  rpeChipSelected: {
    borderColor: colors.accent,
    backgroundColor: colors.accentSoft,
  },
  rpeLabel: {
    ...(typography.bodyStrong as TextStyle),
    color: colors.textSecondary,
  },
  rpeLabelSelected: {
    color: colors.accent,
  },
  notesInput: {
    height: 80,
    paddingTop: spacing.sm,
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

const sportGroupStyles = StyleSheet.create({
  container: {
    gap: spacing.sm,
  },
  label: {
    ...(typography.caption as TextStyle),
    color: colors.textTertiary,
    textTransform: "uppercase",
    letterSpacing: 0.8,
    fontWeight: "600",
  },
  chips: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: spacing.sm,
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
