import type { TextStyle, ViewStyle } from "react-native";

// Paleta neutra + acentos — tom Apple-like, alto contraste com base em cinzas frios
export const colors = Object.freeze({
  // Neutros (gray cool)
  gray50: "#f7f8fa",
  gray100: "#eef0f3",
  gray200: "#e3e6eb",
  gray300: "#cfd3da",
  gray400: "#9aa0a6",
  gray500: "#6b7280",
  gray600: "#4b5563",
  gray700: "#374151",
  gray800: "#1f2937",
  gray900: "#0f172a",

  // Acentos
  accent: "#2563eb",
  accentSoft: "#dbeafe",
  accentMuted: "#eff6ff",
  success: "#10b981",
  successSoft: "#d1fae5",
  warning: "#f59e0b",
  warningSoft: "#fef3c7",
  danger: "#ef4444",
  dangerSoft: "#fee2e2",

  // Aliases semânticos
  background: "#f7f8fa",
  surface: "#ffffff",
  surfaceMuted: "#f1f3f6",
  border: "#e5e7eb",
  borderStrong: "#d1d5db",
  textPrimary: "#0f172a",
  textSecondary: "#4b5563",
  textTertiary: "#9aa0a6",
  textInverse: "#ffffff",
});

export type ColorToken = keyof typeof colors;

// Escalas tipográficas — valores absolutos em px
export const typography = Object.freeze({
  displayLg: { fontSize: 32, lineHeight: 38, fontWeight: "700" } as TextStyle,
  displayMd: { fontSize: 28, lineHeight: 34, fontWeight: "700" } as TextStyle,
  titleLg: { fontSize: 22, lineHeight: 28, fontWeight: "700" } as TextStyle,
  titleMd: { fontSize: 18, lineHeight: 24, fontWeight: "600" } as TextStyle,
  titleSm: { fontSize: 15, lineHeight: 20, fontWeight: "600" } as TextStyle,
  body: { fontSize: 15, lineHeight: 22, fontWeight: "400" } as TextStyle,
  bodyStrong: { fontSize: 15, lineHeight: 22, fontWeight: "600" } as TextStyle,
  bodySm: { fontSize: 13, lineHeight: 18, fontWeight: "400" } as TextStyle,
  caption: { fontSize: 11, lineHeight: 14, fontWeight: "500" } as TextStyle,
  metric: { fontSize: 24, lineHeight: 28, fontWeight: "700" } as TextStyle,
  metricLg: { fontSize: 34, lineHeight: 38, fontWeight: "700" } as TextStyle,
});

export type TypographyToken = keyof typeof typography;

// Escala de espaçamento em múltiplos de 4
export const spacing = Object.freeze({
  xs: 4,
  sm: 8,
  md: 12,
  base: 16,
  lg: 20,
  xl: 24,
  "2xl": 32,
  "3xl": 40,
  "4xl": 48,
});

export type SpacingToken = keyof typeof spacing;

// Raios
export const radii = Object.freeze({
  sm: 6,
  md: 10,
  lg: 16,
  xl: 20,
  pill: 999,
});

export type RadiusToken = keyof typeof radii;

// Sombras iOS-like (sutis)
export const shadows = Object.freeze({
  none: {} as ViewStyle,
  sm: {
    shadowColor: "#0f172a",
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 1,
  } satisfies ViewStyle,
  md: {
    shadowColor: "#0f172a",
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.06,
    shadowRadius: 12,
    elevation: 3,
  } satisfies ViewStyle,
  lg: {
    shadowColor: "#0f172a",
    shadowOffset: { width: 0, height: 10 },
    shadowOpacity: 0.1,
    shadowRadius: 24,
    elevation: 6,
  } satisfies ViewStyle,
});

export type ShadowToken = keyof typeof shadows;
