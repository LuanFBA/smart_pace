import { useEffect, useState } from "react";
import { ActivityIndicator, StyleSheet, View } from "react-native";
import * as SecureStore from "expo-secure-store";
import { router } from "expo-router";

import { useAuthStore } from "../src/stores/auth-store";

const ACCESS_TOKEN_KEY = "access_token";
const REFRESH_TOKEN_KEY = "refresh_token";
const ATHLETE_PROFILE_ID_KEY = "athlete_profile_id";
const FULL_NAME_KEY = "full_name";

export default function Index() {
  const [isHydrating, setIsHydrating] = useState(true);
  const setTokens = useAuthStore((state) => state.setTokens);
  const setAthleteProfileId = useAuthStore(
    (state) => state.setAthleteProfileId,
  );
  const setFullName = useAuthStore((state) => state.setFullName);
  const setHydrated = useAuthStore((state) => state.setHydrated);

  useEffect(() => {
    async function hydrate() {
      const accessToken = await SecureStore.getItemAsync(ACCESS_TOKEN_KEY);
      const refreshToken = await SecureStore.getItemAsync(REFRESH_TOKEN_KEY);
      const athleteProfileId = await SecureStore.getItemAsync(
        ATHLETE_PROFILE_ID_KEY,
      );
      const fullName = await SecureStore.getItemAsync(FULL_NAME_KEY);

      if (accessToken && refreshToken) {
        setTokens({
          access_token: accessToken,
          refresh_token: refreshToken,
          token_type: "bearer",
        });
        if (athleteProfileId) {
          setAthleteProfileId(athleteProfileId);
        }
        if (fullName) {
          setFullName(fullName);
        }
        setHydrated();
        router.replace("/(app)/dashboard");
      } else {
        setHydrated();
        router.replace("/(auth)/login");
      }

      setIsHydrating(false);
    }

    hydrate();
  }, [setTokens, setAthleteProfileId, setFullName, setHydrated]);

  if (isHydrating) {
    return (
      <View style={styles.container}>
        <ActivityIndicator size="large" color="#2563eb" />
      </View>
    );
  }

  return null;
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: "#ffffff",
  },
});
