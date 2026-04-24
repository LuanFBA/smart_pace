import { useEffect, useState } from "react";

import { getMyProfile } from "../services/auth-service";
import { ApiError, type AthleteProfile } from "../types/api";

interface UseProfileResult {
  profile: AthleteProfile | null;
  isLoading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

export function useProfile(): UseProfileResult {
  const [profile, setProfile] = useState<AthleteProfile | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchProfile = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await getMyProfile();
      setProfile(data);
    } catch (e) {
      if (e instanceof ApiError && e.status === 404) {
        // Usuário ainda não criou perfil de atleta — estado válido
        setProfile(null);
      } else {
        setError("Não foi possível carregar o perfil.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchProfile();
  }, []);

  return { profile, isLoading, error, refetch: fetchProfile };
}
