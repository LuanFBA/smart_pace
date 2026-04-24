import { StyleSheet, View, type ViewStyle } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";

import { colors, spacing } from "../theme";

interface ScreenProps {
  children: React.ReactNode;
  // Quando true, desativa o padding horizontal padrão — útil para telas
  // com conteúdos edge-to-edge (ex.: header com gradiente de borda a borda)
  noPadding?: boolean;
  // Sobrescreve o fundo padrão
  backgroundColor?: string;
  style?: ViewStyle;
  // Controla áreas seguras — default: top/bottom/left/right
  edges?: ("top" | "bottom" | "left" | "right")[];
}

export function Screen({
  children,
  noPadding = false,
  backgroundColor = colors.background,
  style,
  edges = ["top", "bottom", "left", "right"],
}: ScreenProps) {
  return (
    <SafeAreaView
      edges={edges}
      style={[styles.root, { backgroundColor }, style]}
    >
      <View style={noPadding ? styles.flex : styles.content}>{children}</View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  root: {
    flex: 1,
  },
  flex: {
    flex: 1,
  },
  content: {
    flex: 1,
    paddingHorizontal: spacing.xl,
  },
});
