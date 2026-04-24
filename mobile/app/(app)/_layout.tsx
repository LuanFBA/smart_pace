import { useEffect } from "react";
import { router, Stack } from "expo-router";
import { StatusBar } from "expo-status-bar";

import { useAuthStore } from "../../src/stores/auth-store";

export default function AppLayout() {
  const accessToken = useAuthStore((state) => state.accessToken);

  // Redireciona para login se não estiver autenticado
  useEffect(() => {
    if (accessToken === null) {
      router.replace("/(auth)/login");
    }
  }, [accessToken]);

  return (
    <>
      <StatusBar style="auto" />
      <Stack screenOptions={{ headerShown: false }} />
    </>
  );
}
