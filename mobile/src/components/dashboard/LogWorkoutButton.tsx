import { ChevronRight, Plus } from "lucide-react-native";
import { Pressable, StyleSheet, Text, View, type TextStyle } from "react-native";
import Animated, {
  useAnimatedStyle,
  useSharedValue,
  withTiming,
} from "react-native-reanimated";
import { LinearGradient } from "expo-linear-gradient";

import { radii, shadows, spacing, typography } from "../../theme";

interface LogWorkoutButtonProps {
  onPress: () => void;
}

const AnimatedPressable = Animated.createAnimatedComponent(Pressable);

export function LogWorkoutButton({ onPress }: LogWorkoutButtonProps) {
  const scale = useSharedValue(1);

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ scale: scale.value }],
  }));

  return (
    <AnimatedPressable
      onPress={onPress}
      onPressIn={() => { scale.value = withTiming(0.97, { duration: 90 }); }}
      onPressOut={() => { scale.value = withTiming(1, { duration: 140 }); }}
      style={animatedStyle}
    >
      <LinearGradient
        colors={["#1d4ed8", "#2563eb", "#3b82f6"]}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 1 }}
        style={[styles.card, shadows.lg]}
      >
        {/* Ícone em círculo */}
        <View style={styles.iconCircle}>
          <Plus color="#2563eb" size={22} strokeWidth={2.5} />
        </View>

        {/* Texto */}
        <View style={styles.textBlock}>
          <Text style={styles.title}>Registrar treino</Text>
          <Text style={styles.subtitle}>Adicione um treino realizado</Text>
        </View>

        {/* Seta */}
        <ChevronRight color="rgba(255,255,255,0.7)" size={20} strokeWidth={2} />
      </LinearGradient>
    </AnimatedPressable>
  );
}

const styles = StyleSheet.create({
  card: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.md,
    paddingVertical: spacing.base,
    paddingHorizontal: spacing.lg,
    borderRadius: radii.lg,
  },
  iconCircle: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: "rgba(255,255,255,0.92)",
    alignItems: "center",
    justifyContent: "center",
  },
  textBlock: {
    flex: 1,
    gap: 2,
  },
  title: {
    ...(typography.titleSm as TextStyle),
    color: "#ffffff",
  },
  subtitle: {
    ...(typography.bodySm as TextStyle),
    color: "rgba(255,255,255,0.75)",
  },
});
