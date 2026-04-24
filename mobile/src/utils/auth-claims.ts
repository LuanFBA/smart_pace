// Decodifica o payload de um JWT (compatível com Hermes — sem atob)
function decodePayload(token: string): Record<string, unknown> | null {
  try {
    const base64 = token.split(".")[1];
    if (!base64) return null;

    const chars =
      "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=";
    let output = "";
    let buffer = 0;
    let bits = 0;

    for (const char of base64.replace(/-/g, "+").replace(/_/g, "/")) {
      const index = chars.indexOf(char);
      if (index === -1) continue;
      buffer = (buffer << 6) | index;
      bits += 6;
      if (bits >= 8) {
        bits -= 8;
        output += String.fromCharCode((buffer >> bits) & 0xff);
      }
    }

    return JSON.parse(output) as Record<string, unknown>;
  } catch {
    return null;
  }
}

export interface AuthIdentity {
  name: string | null;
  email: string | null;
}

// Extrai identidade legível a partir do access token, tentando claims comuns
// (full_name, name, email). Retorna nulls quando não houver dados.
export function readIdentityFromToken(
  token: string | null | undefined,
): AuthIdentity {
  if (!token) return { name: null, email: null };

  const payload = decodePayload(token);
  if (!payload) return { name: null, email: null };

  const name =
    typeof payload.full_name === "string"
      ? payload.full_name
      : typeof payload.name === "string"
        ? payload.name
        : null;
  const email = typeof payload.email === "string" ? payload.email : null;

  return { name, email };
}
