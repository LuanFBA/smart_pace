import Constants from "expo-constants";
import { router } from "expo-router";

import { useAuthStore } from "../stores/auth-store";
import { ApiError, type AuthTokens } from "../types/api";

const BASE_URL: string =
  (Constants.expoConfig?.extra?.apiBaseUrl as string | undefined) ??
  "http://localhost:8000/api/v1";

// Mutex para evitar múltiplos refreshes concorrentes
let refreshPromise: Promise<AuthTokens> | null = null;

async function refreshAccessToken(): Promise<AuthTokens> {
  const { refreshToken } = useAuthStore.getState();
  if (!refreshToken) {
    throw new ApiError(401, "No refresh token available");
  }

  const response = await fetch(`${BASE_URL}/auth/token/refresh`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh_token: refreshToken }),
  });

  if (!response.ok) {
    throw new ApiError(response.status, "Token refresh failed");
  }

  return (await response.json()) as AuthTokens;
}

function handleSessionExpired(): void {
  useAuthStore.getState().clear();
  router.replace("/(auth)/login");
}

export async function apiRequest<T>(
  endpoint: string,
  options?: RequestInit & { authenticated?: boolean },
): Promise<T> {
  const { authenticated = false, ...fetchOptions } = options ?? {};

  const headers = new Headers(fetchOptions.headers);
  if (!headers.has("Content-Type") && fetchOptions.body) {
    headers.set("Content-Type", "application/json");
  }

  if (authenticated) {
    const { accessToken } = useAuthStore.getState();
    if (accessToken) {
      headers.set("Authorization", `Bearer ${accessToken}`);
    }
  }

  let response: Response;
  try {
    response = await fetch(`${BASE_URL}${endpoint}`, {
      ...fetchOptions,
      headers,
    });
  } catch {
    throw new ApiError(0, "Network error");
  }

  // Tenta refresh se receber 401 em rota autenticada
  if (response.status === 401 && authenticated) {
    try {
      // Usa mutex — se já existe um refresh em andamento, espera o mesmo
      if (!refreshPromise) {
        refreshPromise = refreshAccessToken();
      }
      const newTokens = await refreshPromise;
      useAuthStore.getState().setTokens(newTokens);

      // Reexecuta a requisição original com o novo token
      headers.set(
        "Authorization",
        `Bearer ${newTokens.access_token}`,
      );
      const retryResponse = await fetch(`${BASE_URL}${endpoint}`, {
        ...fetchOptions,
        headers,
      });

      if (!retryResponse.ok) {
        const body = await retryResponse.text();
        const detail = parseErrorDetail(body);
        throw new ApiError(retryResponse.status, detail);
      }

      return (await retryResponse.json()) as T;
    } catch (error) {
      if (error instanceof ApiError && error.status !== 401) {
        throw error;
      }
      // Refresh falhou — desloga o usuário
      handleSessionExpired();
      throw new ApiError(401, "Session expired");
    } finally {
      refreshPromise = null;
    }
  }

  if (!response.ok) {
    const body = await response.text();
    const detail = parseErrorDetail(body);
    throw new ApiError(response.status, detail);
  }

  // 204 No Content — sem body
  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}

// Extrai mensagem de erro do body (FastAPI usa { "detail": "..." })
function parseErrorDetail(body: string): string {
  try {
    const parsed = JSON.parse(body) as { detail?: string };
    return parsed.detail ?? body;
  } catch {
    return body || "Unknown error";
  }
}
