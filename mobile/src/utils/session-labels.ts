import {
  Activity,
  Bike,
  Footprints,
  Gauge,
  Mountain,
  Repeat,
  Waves,
  type LucideIcon,
} from "lucide-react-native";

import type { SessionType } from "../types/api";

// Rótulos pt-BR para os tipos de sessão
export const SESSION_TYPE_LABELS: Record<SessionType, string> = {
  easy_run: "Corrida leve",
  tempo: "Tempo run",
  interval: "Intervalado",
  long_run: "Corrida longa",
  recovery: "Recuperação",
  cycling_endurance: "Ciclismo resistência",
  cycling_interval: "Ciclismo intervalado",
};

// Ícones associados a cada tipo de sessão (lucide)
export const SESSION_TYPE_ICONS: Record<SessionType, LucideIcon> = {
  easy_run: Footprints,
  tempo: Gauge,
  interval: Repeat,
  long_run: Mountain,
  recovery: Waves,
  cycling_endurance: Bike,
  cycling_interval: Bike,
};

// Fallback quando o backend envia algo inesperado
export const FALLBACK_SESSION_ICON: LucideIcon = Activity;

// Descrição curta complementar (usada em cards detalhados)
export const SESSION_TYPE_DESCRIPTIONS: Record<SessionType, string> = {
  easy_run: "Ritmo confortável para recuperação aeróbica",
  tempo: "Ritmo sustentado próximo ao limiar",
  interval: "Tiros curtos em alta intensidade",
  long_run: "Volume elevado em ritmo moderado",
  recovery: "Sessão muito leve para recuperação ativa",
  cycling_endurance: "Pedalada longa em zona aeróbica",
  cycling_interval: "Pedalada com intervalos intensos",
};
