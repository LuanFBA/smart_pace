import { useCallback, useState } from "react";
import { router } from "expo-router";

import * as authService from "../services/auth-service";
import { useAuthStore } from "../stores/auth-store";
import { ApiError } from "../types/api";

interface UseAuthReturn {
  login: (email: string, password: string) => Promise<void>;
  register: (
    fullName: string,
    email: string,
    password: string,
  ) => Promise<void>;
  logout: () => Promise<void>;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

export function useAuth(): UseAuthReturn {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const accessToken = useAuthStore((state) => state.accessToken);
  const setTokens = useAuthStore((state) => state.setTokens);
  const setAthleteProfileId = useAuthStore(
    (state) => state.setAthleteProfileId,
  );
  const setFullName = useAuthStore((state) => state.setFullName);
  const clear = useAuthStore((state) => state.clear);

  // Busca o perfil do atleta após autenticação
  const fetchProfile = useCallback(async () => {
    try {
      const profile = await authService.getMyProfile();
      setAthleteProfileId(profile.id);
      if (profile.user_full_name) {
        setFullName(profile.user_full_name);
      }
    } catch (err) {
      // Usuário recém-registrado pode não ter perfil (404) — ignora
      if (!(err instanceof ApiError && err.status === 404)) {
        throw err;
      }
    }
  }, [setAthleteProfileId, setFullName]);

  const login = useCallback(
    async (email: string, password: string) => {
      setIsLoading(true);
      setError(null);
      try {
        const tokens = await authService.login(email, password);
        setTokens(tokens);
        await fetchProfile();
        router.replace("/(app)/dashboard");
      } catch (err) {
        const message =
          err instanceof ApiError ? err.message : "Erro inesperado";
        setError(message);
      } finally {
        setIsLoading(false);
      }
    },
    [setTokens, fetchProfile],
  );

  const register = useCallback(
    async (fullName: string, email: string, password: string) => {
      setIsLoading(true);
      setError(null);
      try {
        const tokens = await authService.register(email, password, fullName);
        setTokens(tokens);
        await fetchProfile();
        router.replace("/(app)/dashboard");
      } catch (err) {
        const message =
          err instanceof ApiError ? err.message : "Erro inesperado";
        setError(message);
      } finally {
        setIsLoading(false);
      }
    },
    [setTokens, fetchProfile],
  );

  const logout = useCallback(async () => {
    clear();
    router.replace("/(auth)/login");
  }, [clear]);

  return {
    login,
    register,
    logout,
    isAuthenticated: accessToken !== null,
    isLoading,
    error,
  };
}
