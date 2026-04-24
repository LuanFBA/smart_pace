import { Tabs } from "expo-router";
import { History, LayoutDashboard, Plus, User } from "lucide-react-native";

import { colors } from "../../../src/theme";

export default function TabsLayout() {
  return (
    <Tabs
      screenOptions={{
        headerShown: false,
        tabBarActiveTintColor: colors.accent,
        tabBarInactiveTintColor: colors.textTertiary,
        tabBarStyle: {
          backgroundColor: colors.surface,
          borderTopColor: colors.border,
          borderTopWidth: 1,
        },
      }}
    >
      <Tabs.Screen
        name="activity-history"
        options={{
          title: "Histórico",
          tabBarIcon: ({ color, size }) => (
            <History color={color} size={size} strokeWidth={2} />
          ),
        }}
      />
      <Tabs.Screen
        name="dashboard"
        options={{
          title: "Início",
          tabBarIcon: ({ color, size }) => (
            <LayoutDashboard color={color} size={size} strokeWidth={2} />
          ),
        }}
      />
      <Tabs.Screen
        name="log-workout"
        options={{
          title: "Registrar",
          tabBarIcon: ({ color, size }) => (
            <Plus color={color} size={size} strokeWidth={2.25} />
          ),
        }}
      />
      <Tabs.Screen
        name="profile"
        options={{
          title: "Perfil",
          tabBarIcon: ({ color, size }) => (
            <User color={color} size={size} strokeWidth={2} />
          ),
        }}
      />
    </Tabs>
  );
}
