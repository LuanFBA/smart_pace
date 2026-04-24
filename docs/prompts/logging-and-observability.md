# SDD — Logging Estruturado e Observabilidade

## Contexto

O smart_pace é uma plataforma FastAPI com Clean Architecture (Domain / Application / Infrastructure / Interface).
A infraestrutura roda no Google Cloud Platform (Cloud Run + Cloud SQL).
Atualmente não existe nenhuma instrumentação de logging ou tracing.

Stack relevante:
- Python 3.12
- FastAPI + uvicorn
- SQLAlchemy 2.x async
- pyproject.toml com `uv` como package manager
- Ponto de entrada: `backend/src/smart_pace/interface/main.py`
- Configurações centralizadas em `backend/src/smart_pace/infrastructure/settings.py` (pydantic-settings, prefixo `SMART_PACE_`)
- Container de DI manual em `backend/src/smart_pace/infrastructure/container.py`

---

## Objetivo

Implementar logging estruturado (JSON) e setup inicial de OpenTelemetry com os seguintes exporters:
- **Traces:** OTLP (HTTP) → compatível com Google Cloud Trace
- **Logs:** integrado ao logging estruturado Python
- **Métricas:** fora do escopo desta tarefa

---

## Não está no escopo

- Instrumentação manual de spans nos use cases
- Métricas (OpenTelemetry Metrics API)
- Configuração de dashboards ou alertas
- Mudar o comportamento funcional de qualquer camada existente

---

## Restrições do projeto (CLAUDE.md)

- Código em inglês, comentários em português
- Tipagem forte em todo o código novo
- Sem lógica de negócio fora do domínio
- Sem estado global — configuração via injeção ou lifespan do FastAPI
- Sem side effects ocultos

---

## Design

### 1. Logging estruturado

Usar `structlog` com renderer JSON para produção e renderer colorido para desenvolvimento.

O logger deve ser configurado **uma única vez** no startup (`lifespan` em `main.py`).
Após a configuração, qualquer módulo obtém o logger via `structlog.get_logger()`.

Campos obrigatórios em todo log:
- `timestamp` (ISO 8601)
- `level`
- `service` = `"smart_pace"`
- `environment` (vindo de `Settings`)
- `trace_id` e `span_id` quando dentro de um span OpenTelemetry ativo

### 2. Middleware de request logging

Um middleware ASGI (não FastAPI middleware) deve logar cada request/response com:
- `method`, `path`, `status_code`, `duration_ms`
- `trace_id` propagado do header `traceparent` (W3C Trace Context)

Não logar o body — apenas metadados.

### 3. OpenTelemetry

Usar auto-instrumentação para FastAPI e SQLAlchemy via:
- `opentelemetry-instrumentation-fastapi`
- `opentelemetry-instrumentation-sqlalchemy`

Exporter: OTLP HTTP (`opentelemetry-exporter-otlp-proto-http`).
Endpoint configurável via `Settings` com default para `http://localhost:4318`.

O setup do TracerProvider deve ocorrer no `lifespan` do FastAPI, antes do `yield`.
O shutdown do provider deve ocorrer após o `yield`.

### 4. Settings

Adicionar as seguintes variáveis ao `Settings`:

```python
log_level: str = "INFO"
log_format: Literal["json", "console"] = "json"
environment: str = "production"
otel_enabled: bool = True
otel_exporter_otlp_endpoint: str = "http://localhost:4318"
otel_service_name: str = "smart_pace"
```

### 5. Localização dos arquivos novos

```
backend/src/smart_pace/
├── infrastructure/
│   ├── observability/
│   │   ├── __init__.py
│   │   ├── logging.py        # configuração do structlog
│   │   └── tracing.py        # setup do OpenTelemetry TracerProvider
│   └── middleware/
│       ├── __init__.py
│       └── request_logging.py  # middleware ASGI de request/response
```

`main.py` deve importar e chamar as funções de setup no `lifespan`.

---

## Dependências a adicionar em `pyproject.toml`

```toml
"structlog>=24.0",
"opentelemetry-sdk>=1.25",
"opentelemetry-instrumentation-fastapi>=0.46b0",
"opentelemetry-instrumentation-sqlalchemy>=0.46b0",
"opentelemetry-exporter-otlp-proto-http>=1.25",
```

---

## Critérios de Aceite

- [ ] `uv sync` instala todas as dependências sem conflito
- [ ] Em desenvolvimento (`log_format=console`), os logs são legíveis no terminal
- [ ] Em produção (`log_format=json`), cada linha de log é um JSON válido com os campos obrigatórios
- [ ] Todo request HTTP gera uma linha de log com `method`, `path`, `status_code`, `duration_ms`
- [ ] Com `otel_enabled=true`, o `traceparent` do header de entrada é propagado corretamente e aparece nos logs como `trace_id`
- [ ] Com `otel_enabled=false`, nenhuma dependência OTel é inicializada e a aplicação sobe normalmente
- [ ] Nenhuma camada de domínio importa `structlog` ou qualquer lib de observabilidade
- [ ] O `Container` não precisa ser alterado
- [ ] `pytest` continua passando sem configuração adicional

---

## Exemplo de log esperado (produção)

```json
{
  "timestamp": "2026-04-10T14:32:01.123Z",
  "level": "info",
  "service": "smart_pace",
  "environment": "production",
  "event": "request_finished",
  "method": "POST",
  "path": "/api/v1/workouts/sessions",
  "status_code": 201,
  "duration_ms": 42,
  "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
  "span_id": "00f067aa0ba902b7"
}
```
