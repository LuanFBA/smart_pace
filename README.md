# smart_pace

**Plataforma de Treinos Inteligentes** — sistema para registro, análise e sugestão de treinos de corrida e ciclismo.

---

## Casos de Uso

```mermaid
graph LR
    Atleta([Atleta])

    subgraph smart_pace

        subgraph Autenticação
            UC1(Registrar conta)
            UC2(Fazer login)
            UC3(Renovar token)
            UC4(Desativar conta)
        end

        subgraph Perfil
            UC5(Criar perfil de atleta)
            UC6(Atualizar dados de FC)
            UC7(Ver zonas de FC)
        end

        subgraph Plano de Treino
            UC8(Criar plano de treino)
            UC9(Ativar plano)
            UC10(Cancelar plano)
        end

        subgraph Sessões
            UC11(Registrar sessão de treino)
            UC12(Consultar histórico de treinos)
            UC13(Obter sugestão do próximo treino)
        end

        subgraph Métricas
            UC14(Ver dashboard de evolução)
        end

        %% include: comportamentos internos disparados automaticamente
        UC6 -.->|include| UC7
        UC11 -.->|include| UC14

    end

    Atleta --> UC1
    Atleta --> UC2
    Atleta --> UC3
    Atleta --> UC4
    Atleta --> UC5
    Atleta --> UC6
    Atleta --> UC8
    Atleta --> UC9
    Atleta --> UC10
    Atleta --> UC11
    Atleta --> UC12
    Atleta --> UC13
    Atleta --> UC14
```

---

## Diagramas de Atividade

### Registro e Configuração Inicial

```mermaid
flowchart TD
    A([Início]) --> B[Informar nome, email e senha]
    B --> C{Email já cadastrado?}
    C -- Sim --> D[Retornar erro 409 Conflict]
    D --> B
    C -- Não --> E[Criar conta e gerar JWT]
    E --> F[Informar esporte, FC máxima e FC de repouso]
    F --> G{Dados válidos?\nFC repouso < FC máxima?}
    G -- Não --> H[Retornar erro de validação]
    H --> F
    G -- Sim --> I[Criar perfil de atleta]
    I --> J[Calcular 5 zonas de FC - Karvonen]
    J --> K([Perfil pronto para uso])
```

---

### Criação e Ativação de Plano de Treino

```mermaid
flowchart TD
    A([Atleta autenticado]) --> B[Informar nome, objetivo, datas e esporte]
    B --> C{Data final após data inicial?}
    C -- Não --> D[Retornar erro de validação]
    D --> B
    C -- Sim --> E[Criar plano com status DRAFT]
    E --> F[Adicionar blocos de treino por fase BASE · BUILD · PEAK · TAPER]
    F --> G[Solicitar ativação do plano]
    G --> H{Status é DRAFT?}
    H -- Não --> I[Retornar erro: transição inválida]
    H -- Sim --> J[Mudar status para ACTIVE]
    J --> K([Plano ativo])
```

---

### Registro de Sessão de Treino

```mermaid
flowchart TD
    A([Atleta com plano ativo]) --> B[Informar distância, duração,\nFC média e percepção de esforço]
    B --> C{Dados válidos?\nFC média ≤ FC máxima\nRPE entre 1 e 10?}
    C -- Não --> D[Retornar erro de validação]
    D --> B
    C -- Sim --> E[Calcular pace médio\ndistância ÷ duração]
    E --> F[Registrar WorkoutLog]
    F --> G[Marcar WorkoutSession como COMPLETED]
    G --> H[Recalcular CTL e ATL]
    H --> I([Treino registrado])
```

---

### Sugestão do Próximo Treino

```mermaid
flowchart TD
    A([Atleta solicita sugestão]) --> B[Buscar última sessão concluída]
    B --> C{Existe histórico?}
    C -- Não --> D[Sugerir treino leve inicial\nEASY_RUN ou CYCLING_ENDURANCE]
    C -- Sim --> E{Tipo da última sessão}
    E -- INTERVAL ou LONG_RUN --> F[Sugerir RECOVERY]
    E -- TEMPO --> G[Sugerir EASY_RUN]
    E -- EASY_RUN --> H[Sugerir TEMPO]
    E -- RECOVERY --> I[Sugerir EASY_RUN]
    D --> J([Retornar tipo sugerido])
    F --> J
    G --> J
    H --> J
    I --> J
```

---

### Cálculo de Zonas de Frequência Cardíaca

```mermaid
flowchart TD
    A([FC máxima e FC de repouso disponíveis]) --> B[Calcular FC de reserva\nFCR = FCmax - FCrepouso]
    B --> C[Zona 1 - Recovery\nFCrepouso + FCR × 50% a 60%]
    C --> D[Zona 2 - Aerobic\nFCrepouso + FCR × 60% a 70%]
    D --> E[Zona 3 - Tempo\nFCrepouso + FCR × 70% a 80%]
    E --> F[Zona 4 - Threshold\nFCrepouso + FCR × 80% a 90%]
    F --> G[Zona 5 - VO2max\nFCrepouso + FCR × 90% a 100%]
    G --> H([5 zonas calculadas])
```

---

## Arquitetura

O projeto segue **Clean Architecture** com separação estrita em quatro camadas:

```
smart_pace/
├── domain/          # Regras de negócio puras (stdlib only)
│   ├── entities/    # User, AthleteProfile, TrainingPlan, WorkoutLog...
│   ├── value_objects/  # Pace, Distance, Duration, HeartRate, Vo2max...
│   ├── repositories/   # Interfaces ABC (sem I/O)
│   └── services/    # TrainingZoneCalculator, WorkoutSuggestionEngine
├── application/     # Orquestração de casos de uso
├── infrastructure/  # PostgreSQL, JWT, OTel (implementações)
└── interface/       # FastAPI REST (MVP) · gRPC (futuro)
```

**Stack:** FastAPI · PostgreSQL · SQLAlchemy 2.x async · Pydantic v2 · OpenTelemetry · GCP Cloud Run

---

## Setup Local

```bash
cp .env.example .env
make setup    # instala dependências (uv)
make dev      # sobe PostgreSQL + backend
# → http://localhost:8000/docs
```

## Testes

```bash
make test     # unit + integration (Testcontainers)
make lint     # ruff + mypy
```
