// Funções puras de formatação compartilhadas entre telas e componentes

// Converte segundos para HH:MM:SS (ou MM:SS quando < 1h)
export function formatDuration(totalSeconds: number): string {
  const safe = Math.max(0, Math.floor(totalSeconds));
  const hours = Math.floor(safe / 3600);
  const minutes = Math.floor((safe % 3600) / 60);
  const seconds = safe % 60;
  const mm = String(minutes).padStart(2, "0");
  const ss = String(seconds).padStart(2, "0");
  return hours > 0 ? `${hours}:${mm}:${ss}` : `${mm}:${ss}`;
}

// Duração compacta: "1h 23min" ou "45min"
export function formatDurationCompact(totalSeconds: number): string {
  const safe = Math.max(0, Math.floor(totalSeconds));
  const hours = Math.floor(safe / 3600);
  const minutes = Math.floor((safe % 3600) / 60);
  if (hours === 0) return `${minutes}min`;
  if (minutes === 0) return `${hours}h`;
  return `${hours}h ${minutes}min`;
}

// Converte metros para km (string com 2 casas decimais, vírgula como separador)
export function metersToKm(meters: number, decimals = 2): string {
  return (meters / 1000).toFixed(decimals).replace(".", ",");
}

// Converte distância (metros) e duração (segundos) para velocidade em km/h: "X,X"
export function formatSpeed(distanceMeters: number, durationSeconds: number): string {
  if (durationSeconds <= 0) return "0,0";
  const kmh = (distanceMeters / 1000) / (durationSeconds / 3600);
  return kmh.toFixed(1).replace(".", ",");
}

// Formata pace de segundos/km para mm:ss
export function formatPace(secondsPerKm: number): string {
  if (!Number.isFinite(secondsPerKm) || secondsPerKm <= 0) return "--:--";
  const minutes = Math.floor(secondsPerKm / 60);
  const seconds = Math.floor(secondsPerKm % 60);
  return `${minutes}:${String(seconds).padStart(2, "0")}`;
}

// Formata data ISO para DD/MM/YYYY
// Parseia a string diretamente para evitar problemas de timezone:
// new Date("1990-05-15") é interpretado como UTC midnight, o que em fusos
// negativos (ex: UTC-3) resulta no dia anterior.
export function formatDate(isoDate: string): string {
  const [year, month, day] = isoDate.split("T")[0].split("-");
  return `${day}/${month}/${year}`;
}

// Data relativa curta em pt-BR: "Hoje", "Ontem", "há N dias", ou DD/MM
export function formatRelativeDate(isoDate: string, reference = new Date()): string {
  const date = new Date(isoDate);
  const startOfDay = (d: Date) =>
    new Date(d.getFullYear(), d.getMonth(), d.getDate()).getTime();
  const diffDays = Math.floor(
    (startOfDay(reference) - startOfDay(date)) / (1000 * 60 * 60 * 24),
  );

  if (diffDays === 0) return "Hoje";
  if (diffDays === 1) return "Ontem";
  if (diffDays > 1 && diffDays < 7) return `há ${diffDays} dias`;
  return formatDate(isoDate);
}

// Número da semana ISO 8601 (segunda como primeiro dia)
export function getIsoWeek(date: Date): number {
  const target = new Date(date.valueOf());
  const dayNr = (date.getDay() + 6) % 7;
  target.setDate(target.getDate() - dayNr + 3);
  const firstThursday = target.valueOf();
  target.setMonth(0, 1);
  if (target.getDay() !== 4) {
    target.setMonth(0, 1 + ((4 - target.getDay() + 7) % 7));
  }
  return 1 + Math.ceil((firstThursday - target.valueOf()) / 604800000);
}

// Extrai iniciais a partir de nome completo ou email
export function extractInitials(source: string | null | undefined): string {
  if (!source) return "?";
  const trimmed = source.trim();
  if (!trimmed) return "?";

  // Email → usa o local-part
  const base = trimmed.includes("@") ? trimmed.split("@")[0] : trimmed;
  const parts = base.split(/[\s._-]+/).filter(Boolean);

  if (parts.length === 0) return trimmed.charAt(0).toUpperCase();
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
  return (parts[0].charAt(0) + parts[parts.length - 1].charAt(0)).toUpperCase();
}

// Saudação por período do dia
export function greetingByHour(hour: number): string {
  if (hour >= 5 && hour < 12) return "Bom dia";
  if (hour >= 12 && hour < 18) return "Boa tarde";
  return "Boa noite";
}
