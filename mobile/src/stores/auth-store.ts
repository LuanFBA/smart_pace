import * as SecureStore from "expo-secure-store";
import { create } from "zustand";

import type { AuthTokens } from "../types/api";

const ACCESS_TOKEN_KEY = "access_token";
const REFRESH_TOKEN_KEY = "refresh_token";
const ATHLETE_PROFILE_ID_KEY = "athlete_profile_id";
const FULL_NAME_KEY = "full_name";

// Decodifica o payload de um JWT sem depender de atob (pode não existir no Hermes)
function decodeJwtPayload(token: string): Record<string, unknown> {
  const base64 = token.split(".")[1];
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
}

export interface AuthState {
  accessToken: string | null;
  refreshToken: string | null;
  userId: string | null;
  athleteProfileId: string | null;
  fullName: string | null;
  isHydrated: boolean;

  setTokens: (tokens: AuthTokens) => void;
  setAthleteProfileId: (id: string) => void;
  setFullName: (name: string) => void;
  setHydrated: () => void;
  clear: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  accessToken: null,
  refreshToken: null,
  userId: null,
  athleteProfileId: null,
  fullName: null,
  isHydrated: false,

  setTokens: (tokens: AuthTokens) => {
    // Persiste tokens no SecureStore
    SecureStore.setItemAsync(ACCESS_TOKEN_KEY, tokens.access_token);
    SecureStore.setItemAsync(REFRESH_TOKEN_KEY, tokens.refresh_token);

    // Extrai userId do payload JWT (claim "sub")
    let userId: string | null = null;
    try {
      const payload = decodeJwtPayload(tokens.access_token);
      userId = typeof payload.sub === "string" ? payload.sub : null;
    } catch {
      // Token mal-formado — ignora a extração do userId
    }

    set({
      accessToken: tokens.access_token,
      refreshToken: tokens.refresh_token,
      userId,
    });
  },

  setAthleteProfileId: (id: string) => {
    SecureStore.setItemAsync(ATHLETE_PROFILE_ID_KEY, id);
    set({ athleteProfileId: id });
  },

  setFullName: (name: string) => {
    SecureStore.setItemAsync(FULL_NAME_KEY, name);
    set({ fullName: name });
  },

  setHydrated: () => {
    set({ isHydrated: true });
  },

  clear: () => {
    SecureStore.deleteItemAsync(ACCESS_TOKEN_KEY);
    SecureStore.deleteItemAsync(REFRESH_TOKEN_KEY);
    SecureStore.deleteItemAsync(ATHLETE_PROFILE_ID_KEY);
    SecureStore.deleteItemAsync(FULL_NAME_KEY);
    set({
      accessToken: null,
      refreshToken: null,
      userId: null,
      athleteProfileId: null,
      fullName: null,
    });
  },
}));
