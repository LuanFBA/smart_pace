import { colors, radii, shadows, spacing, typography } from "./tokens";

// Tema único (prepara extensão futura para dark mode)
export const theme = {
  colors,
  typography,
  spacing,
  radii,
  shadows,
} as const;

export type Theme = typeof theme;

// Hook simples — sem Context por enquanto para manter o MVP enxuto
export function useTheme(): Theme {
  return theme;
}

export { colors, radii, shadows, spacing, typography };
export type { ColorToken, RadiusToken, ShadowToken, SpacingToken, TypographyToken } from "./tokens";
