# SDD — Base do App React Native com Expo

## Contexto do projeto

**smart_pace** é uma plataforma de treinos para corrida e ciclismo.
O backend já existe em FastAPI com Clean Architecture e está documentado em `CLAUDE.md`.
Este documento descreve apenas a implementação do **frontend mobile**.

### Backend disponível (base URL: `http://localhost:8000/api/v1`)

**Auth**
```
POST /auth/register   body: { email, password, full_name }         → { access_token, refresh_token, token_type }
POST /auth/login      body: { email, password }                     → { access_token, refresh_token, token_type }
POST /auth/token/refresh  body: { refresh_token }                  → { access_token, refresh_token, token_type }
DELETE /auth/account  Authorization: Bearer <token>                → 204
```

**Perfil**
```
POST /profiles        body: CreateAthleteProfileRequest            → AthleteProfileOutput
GET  /profiles/{id}   Authorization: Bearer <token>                → AthleteProfileOutput
```

**Treinos**
```
POST /workouts/sessions  body: ScheduleWorkoutSessionRequest       → WorkoutSessionOutput
POST /workouts/log       body: LogWorkoutRequest                   → WorkoutLogOutput
GET  /workouts/history   ?athlete_profile_id=&limit=&offset=       → WorkoutHistoryOutput
GET  /workouts/suggestion ?athlete_profile_id=                     → { suggested_session_type }
```

**Tipos relevantes**
```typescript
type SportType = "running" | "cycling"
type SessionType = "easy_run" | "tempo" | "interval" | "long_run" | "recovery" | "cycling_endurance" | "cycling_interval"
type SessionStatus = "scheduled" | "completed" | "skipped" | "partial"

interface AuthTokens { access_token: string; refresh_token: string; token_type: string }
interface AthleteProfile {
  id: string; user_id: string; sport_type: SportType
  date_of_birth: string; resting_heart_rate: number; maximum_heart_rate: number
  functional_threshold_power: number | null; current_vo2max: number | null
  training_experience_years: number; weekly_target_hours: number
  heart_rate_zones: Array<{ name: string; min_bpm: number; max_bpm: number }>
}
interface WorkoutSession {
  id: string; athlete_profile_id: string; scheduled_date: string
  session_type: SessionType; status: SessionStatus
  target_distance_meters: number | null; target_duration_seconds: number | null
  target_min_pace_seconds_per_km: number | null; target_max_pace_seconds_per_km: number | null
}
interface WorkoutLog {
  id: string; workout_session_id: string; started_at: string; finished_at: string
  actual_distance_meters: number; actual_duration_seconds: number
  average_pace_seconds_per_km: number
  average_heart_rate: number | null; maximum_heart_rate: number | null
  perceived_exertion: number | null; notes: string | null
}
```

---

## Objetivo

Implementar a base do app React Native com Expo contendo:
- Estrutura de pastas escalável
- Navegação com `expo-router`
- Tela de login (e registro)
- Tela de dashboard
- Camada de integração com o backend

---

## Não está no escopo

- Telas de criação de perfil de atleta (apenas fluxo pós-login)
- Tela de registro de treino (log workout)
- Componentes de gráficos ou visualizações complexas
- Push notifications
- Modo offline / cache persistente
- Testes automatizados nesta entrega

---

## Restrições

- TypeScript estrito (`strict: true` no tsconfig)
- Sem lógica de negócio nos componentes — apenas apresentação e chamada de hooks
- Sem chamadas diretas ao `fetch` nos componentes — sempre via camada de serviço
- Tokens JWT devem ser armazenados em `SecureStore` (não em AsyncStorage)
- Variáveis de ambiente via `app.config.ts` com `process.env.EXPO_PUBLIC_*`
- Código em inglês, comentários em português

---

## Design

### Estrutura de pastas

```
mobile/
├── app/                        # expo-router — cada arquivo é uma rota
│   ├── (auth)/
│   │   ├── _layout.tsx         # layout sem navegação (sem tab bar)
│   │   ├── login.tsx
│   │   └── register.tsx
│   ├── (app)/
│   │   ├── _layout.tsx         # layout com tab bar (usuário autenticado)
│   │   └── dashboard.tsx
│   └── index.tsx               # redirect: autenticado → dashboard, não → login
├── src/
│   ├── services/               # chamadas HTTP — conhecem a API, retornam tipos
│   │   ├── api-client.ts       # fetch base com injeção de token e refresh automático
│   │   ├── auth-service.ts
│   │   └── workout-service.ts
│   ├── hooks/                  # lógica de estado e efeitos
│   │   ├── use-auth.ts         # login, logout, estado do usuário
│   │   └── use-workout-history.ts
│   ├── stores/                 # estado global leve (Zustand)
│   │   └── auth-store.ts       # tokens + user_id + athlete_profile_id
│   ├── types/
│   │   └── api.ts              # todos os tipos TypeScript espelhando o backend
│   └── components/             # componentes reutilizáveis sem lógica de negócio
│       ├── Button.tsx
│       ├── Input.tsx
│       └── WorkoutCard.tsx
├── app.config.ts
└── tsconfig.json
```

### Gerenciamento de estado

Usar **Zustand** para estado global (tokens, user_id, athlete_profile_id).
Não usar Context API para autenticação — evita re-renders desnecessários.

```typescript
// src/stores/auth-store.ts
interface AuthState {
  accessToken: string | null
  refreshToken: string | null
  userId: string | null
  athleteProfileId: string | null
  setTokens: (tokens: AuthTokens) => void
  setAthleteProfileId: (id: string) => void
  clear: () => void
}
```

### Camada de serviços

`api-client.ts` — wrapper sobre `fetch` que:
1. Injeta `Authorization: Bearer <token>` automaticamente
2. Intercepta respostas `401` e tenta refresh do token uma vez
3. Se o refresh falhar, chama `clear()` na store e redireciona para login
4. Lança erros tipados (`ApiError` com `status` e `message`)

Cada serviço (`auth-service.ts`, `workout-service.ts`) usa o client e retorna tipos do `api.ts`.

### Navegação (expo-router)

`app/index.tsx` verifica o `accessToken` na store:
- Se presente → `router.replace("/(app)/dashboard")`
- Se ausente → `router.replace("/(auth)/login")`

`app/(app)/_layout.tsx` usa `Stack` ou `Tabs`. Para o MVP, `Stack` é suficiente.

### Telas a implementar

**`(auth)/login.tsx`**
- Campos: email, password
- Chama `useAuth().login()`
- Em caso de erro, exibe mensagem inline (não alert)
- Link para tela de registro

**`(auth)/register.tsx`**
- Campos: full_name, email, password
- Chama `useAuth().register()`
- Após registro bem-sucedido, redireciona para dashboard

**`(app)/dashboard.tsx`**
- Exibe: sugestão do próximo treino (`GET /workouts/suggestion`)
- Exibe: últimos 5 treinos do histórico (`GET /workouts/history?limit=5`)
- Mostra estado de loading e erro para cada seção separadamente
- Botão de logout

### Tokens e segurança

Armazenar em `expo-secure-store`:
```typescript
// ao fazer login
await SecureStore.setItemAsync("access_token", tokens.access_token)
await SecureStore.setItemAsync("refresh_token", tokens.refresh_token)

// ao fazer logout
await SecureStore.deleteItemAsync("access_token")
await SecureStore.deleteItemAsync("refresh_token")
```

Ao iniciar o app, ler o token do SecureStore e popular a store Zustand.

---

## Dependências a instalar

```bash
npx create-expo-app mobile --template blank-typescript
cd mobile
npx expo install expo-router expo-secure-store
npx expo install zustand
```

`package.json` relevante:
```json
{
  "main": "expo-router/entry",
  "dependencies": {
    "expo-router": "~4.0",
    "expo-secure-store": "~14.0",
    "zustand": "^5.0"
  }
}
```

`app.config.ts`:
```typescript
export default {
  expo: {
    scheme: "smartpace",
    web: { bundler: "metro" },
    plugins: ["expo-router", "expo-secure-store"],
    extra: {
      apiBaseUrl: process.env.EXPO_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1",
    },
  },
}
```

---

## Critérios de Aceite

- [ ] `npx expo start` sobe sem erros
- [ ] Usuário não autenticado é redirecionado para `/login` ao abrir o app
- [ ] Login com credenciais válidas redireciona para dashboard
- [ ] Login com credenciais inválidas exibe mensagem de erro inline
- [ ] Dashboard exibe sugestão do próximo treino e os últimos 5 treinos
- [ ] Logout limpa tokens do SecureStore e redireciona para login
- [ ] Token expirado dispara refresh automático transparente ao usuário
- [ ] Nenhum componente importa `fetch` diretamente
- [ ] Nenhum token é armazenado em AsyncStorage
- [ ] TypeScript compila sem erros (`npx tsc --noEmit`)

---

## Sugestões de UX para retenção de usuários

Implementar **após** o MVP estar funcional, em ordem de impacto:

1. **Streak de treinos** — exibir no dashboard quantos dias consecutivos o usuário treinou. Funciona como gamificação passiva e é o principal driver de abertura diária do app.

2. **Tela de onboarding** — primeiro acesso guia o usuário pelo preenchimento do perfil de atleta (sport_type, frequências cardíacas). Usuários que completam o perfil têm muito mais chance de retornar.

3. **Notificação de lembrete** — "Você tem um treino agendado hoje" via `expo-notifications`. Implementar só quando houver `WorkoutSession` com status `scheduled` para o dia atual.

4. **Feedback imediato pós-treino** — após registrar um log, mostrar um card de celebração com o pace médio e comparação com o treino anterior do mesmo tipo. Reforço positivo no momento de maior engajamento.

5. **Indicador de carga semanal** — barra de progresso simples no dashboard mostrando horas treinadas vs. `weekly_target_hours` do perfil. Cria senso de progresso sem precisar de backend novo.

6. **Pull-to-refresh no dashboard** — padrão esperado em apps mobile. Ausência frustra usuários e passa impressão de app desatualizado.
