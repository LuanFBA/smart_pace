# Tela de Detalhe de Treino — Edição e Deleção

**Data:** 2026-04-16  
**Status:** Aprovado

---

## Contexto

O histórico de treinos (`activity-history.tsx`) lista `WorkoutCard` items mas não permite acessar nem editar registros individuais. Este spec cobre a adição de uma tela de detalhe com edição inline (toggle view/edit) e deleção com modal de confirmação customizado.

---

## Backend

### Novos endpoints

| Método | Rota | Status |
|--------|------|--------|
| `GET` | `/workouts/logs/{log_id}` | 200 |
| `PUT` | `/workouts/logs/{log_id}` | 200 |
| `DELETE` | `/workouts/logs/{log_id}` | 204 |

### Ownership

Todos os endpoints validam que o `user_id` do token é dono do `athlete_profile_id` vinculado ao log. Retornam 403 se não for.

### Novos DTOs (Application layer)

**`GetWorkoutLogInput`**
```python
log_id: UUID
user_id: UUID
```
Retorna `WorkoutLogOutput` (já existente).

**`UpdateWorkoutLogInput`**
```python
log_id: UUID
user_id: UUID
started_at: datetime
finished_at: datetime
actual_distance_meters: int
actual_duration_seconds: int
average_heart_rate: int | None
maximum_heart_rate: int | None
perceived_exertion: int | None
notes: str | None
average_power_watts: int | None
```
Retorna `WorkoutLogOutput`. O pace é recalculado automaticamente a partir de distância e duração — não é enviado pelo cliente.

**`DeleteWorkoutLogInput`**
```python
log_id: UUID
user_id: UUID
```
Sem retorno (204 No Content).

### Novos schemas (Interface layer)

**`UpdateWorkoutLogRequest`** — espelha `UpdateWorkoutLogInput` sem `log_id` e `user_id` (vêm de path param e token).

### Novos use cases

**`get_workout_log(input)`**
1. Busca log por id — 404 se não encontrado
2. Valida ownership via `athlete_profile_id` do log
3. Busca `session_type` da sessão associada
4. Retorna `WorkoutLogOutput`

**`update_workout_log(input)`**
1. Busca log por id — 404 se não encontrado
2. Valida ownership
3. Reconstrói entidade `WorkoutLog` com novos valores (recalcula pace via `create_with_calculated_pace`)
4. Persiste via `uow.workout_logs.save()`
5. Recalcula métricas de performance (`_recalculate_performance_metrics`)
6. Retorna `WorkoutLogOutput`

**`delete_workout_log(input)`**
1. Busca log por id — 404 se não encontrado
2. Valida ownership
3. Busca sessão associada, reverte status para `scheduled`
4. Persiste sessão atualizada
5. Remove log via `uow.workout_logs.delete(log_id)`
6. Recalcula métricas de performance
7. Commita transação

### Domain repository

Adiciona método abstrato em `WorkoutLogRepository`:
```python
@abstractmethod
async def delete(self, log_id: UUID) -> None: ...
```

Implementação em `SqlAlchemyWorkoutLogRepository`:
```python
async def delete(self, log_id: UUID) -> None:
    model = await self._session.get(WorkoutLogModel, log_id)
    if model:
        await self._session.delete(model)
        await self._session.flush()
```

---

## Frontend

### Navegação

`WorkoutCard` passa a ser envolvido em `Pressable`. Ao tocar:
```ts
router.push("/(app)/workout/" + log.id)
```

A tela fica em `mobile/app/(app)/workout/[id].tsx` — stack screen não-tab, abaixo de `(app)/_layout.tsx`, com botão de voltar nativo.

### Tela `[id].tsx` — estados

```
mount
  └─ loading → skeleton (full screen)
  └─ erro    → mensagem de erro + botão retry
  └─ loaded  → modo view
        ├─ toca ícone lápis (canto superior direito)
        │     └─ modo edit
        │           ├─ Salvar → loading → recebe log atualizado → modo view
        │           └─ Cancelar → descarta estado de edição → modo view
        └─ toca "Excluir treino" (rodapé, vermelho)
              └─ modal de confirmação
                    ├─ "Sim, excluir" → loading → router.back()
                    └─ "Cancelar" → fecha modal
```

### Layout modo view

- **Header**: data completa (DD/MM/YYYY HH:MM) + label do tipo de sessão (azul=corrida, verde=ciclismo)
- **Bloco primário**: distância grande + tempo + pace (corrida) ou velocidade (ciclismo)
- **Bloco métricas (Card flat)**:
  - FC média / FC máxima (se presentes)
  - Potência média em W (se ciclismo e presente)
  - RPE (se presente)
  - Notas (se presente)
- **Botão "Excluir treino"** — variant `danger`, `fullWidth`, ao final do scroll

### Layout modo edit

Mesmos campos transformados em inputs:
- **Data**: Pressable com `DateTimePicker` (mesmo padrão de `log-workout.tsx`)
- **Início**: `TextInput` com máscara HH:MM
- **Duração**: `TextInput` com máscara HH:MM (calculado a partir de `finished_at - started_at`)
- **Distância**: `TextInput` decimal-pad em km
- **FC média / FC máxima**: `TextInput` numeric, opcionais
- **Potência**: `TextInput` numeric, visível apenas quando `session_type` é cycling
- **RPE**: chips 1-10, mesmo componente de `log-workout`
- **Notas**: `TextInput` multiline

Barra ao final: botões "Cancelar" (ghost) e "Salvar" (primary).

### Modal de confirmação de deleção

Card centralizado sobre overlay escuro (mesmo padrão do iOS date picker em `log-workout.tsx`):
```
┌─────────────────────────────┐
│  Excluir treino?            │
│  Esta ação não pode         │
│  ser desfeita.              │
│                             │
│  [Cancelar]  [Sim, excluir] │
└─────────────────────────────┘
```

### Invalidação da lista

Após deleção bem-sucedida: `router.back()` retorna para `activity-history`. A lista recarrega via `useFocusEffect` (já presente na tela de histórico — adicionar se ainda não tiver).

### Novos arquivos

| Arquivo | Descrição |
|---------|-----------|
| `mobile/app/(app)/workout/[id].tsx` | Tela de detalhe |

### Arquivos modificados

| Arquivo | Mudança |
|---------|---------|
| `mobile/src/components/WorkoutCard.tsx` | Envolver em `Pressable`, aceitar prop `onPress` |
| `mobile/src/services/workout-service.ts` | Adicionar `getWorkoutLog`, `updateWorkout`, `deleteWorkout` |
| `mobile/app/(app)/(tabs)/activity-history.tsx` | Adicionar `useFocusEffect` para recarregar após voltar |
| `backend/src/smart_pace/domain/repositories/workout_log_repository.py` | Método `delete` |
| `backend/src/smart_pace/infrastructure/repositories/workout_log_repository.py` | Implementação `delete` |
| `backend/src/smart_pace/application/dtos/workout.py` | 3 novos DTOs de input |
| `backend/src/smart_pace/application/use_cases/workout_use_cases.py` | 3 novos use cases |
| `backend/src/smart_pace/interface/api/workouts.py` | 3 novas rotas |
| `backend/src/smart_pace/interface/api/schemas/schemas.py` | `UpdateWorkoutLogRequest` |

---

## Fora de escopo

- Edição do `session_type` (tipo de treino) — imutável após registro
- Edição do `athlete_profile_id` / `workout_session_id`
- Reordenação ou fusão de logs
