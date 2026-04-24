# 🧠 smart_pace — AI Development Guide

## 📌 Project Overview

**smart_pace** — Intelligent Training Platform

A system for managing, analyzing, and recommending running and cycling workouts based on athlete performance.

---

## 🏗️ Architecture

The system follows **Clean Architecture** principles with strict separation of concerns.

### Layers

- **Domain**
  - Pure business logic
  - Entities, Value Objects, Domain Services
  - No external dependencies

- **Application**
  - Use cases (orchestration only)
  - DTOs (Pydantic v2)
  - Ports (interfaces)

- **Infrastructure**
  - Database (SQLAlchemy async)
  - External services (JWT, hashing, etc.)

- **Interface**
  - FastAPI (REST endpoints)
  - Thin controllers (no business logic)

---

## ⚙️ Tech Stack

- **Backend:** FastAPI (Python)
- **Mobile:** React Native (Expo)
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy 2.x (async)
- **Communication:** REST (MVP) + gRPC (future-ready)
- **Infrastructure:** Google Cloud Platform (Cloud Run, Cloud SQL)
- **Observability:** OpenTelemetry
- **Testing:** pytest
- **Package Manager:** uv (preferred) or pip

---

## 📂 Expected Project Structure

backend/src/smart_pace/
├── domain/
├── application/
├── infrastructure/
└── interface/
---

## 🧩 Development Principles

### General Rules

- Use **full descriptive names** (no abbreviations)
- Code must be written in **English**
- Comments must be in **Portuguese**
- Maintain **strong typing** everywhere
- Prefer **composition over inheritance**

---

### Domain Rules

- Use only **Python standard library**
- Use `@dataclass` (no Pydantic)
- Value Objects must be **immutable (`frozen=True`)**
- All validation must happen in constructors (`__post_init__`)
- No infrastructure dependencies

---

### Application Rules

- Use cases must:
  - Only orchestrate logic
  - Never contain business rules
- DTOs must:
  - Use **Pydantic v2**
  - Contain only primitive types
- Always use **ports (interfaces)** for dependencies
- Código em inglês e comentários em português

---

### Infrastructure Rules

- Use **SQLAlchemy 2.x (async)**
- Do NOT use raw SQL unless strictly necessary
- Implement repositories strictly following domain interfaces
- Manage transactions using **UnitOfWork**

---

### Interface Rules

- Controllers must be **thin**
- No business logic in routes
- Only:
  - Input validation
  - Calling use cases
  - Returning responses

---

### Known Technical Debt

#### DI: Container injected whole into endpoints

**Where:** All route handlers in `interface/api/` receive `Container = Depends(get_container)` and call `container.some_use_cases()` inline.

**Problem:** Endpoints receive the full `Container` instead of only the use case they need. This breaks the principle of least privilege — a workouts endpoint can access `auth_use_cases()` without needing it. It also makes test setup noisier and endpoint signatures less expressive.

**Correct approach (not yet implemented):**
```python
# dependencies.py
def get_workout_use_cases(container: Container = Depends(get_container)) -> WorkoutUseCases:
    return container.workout_use_cases()

# route
async def schedule_session(
    use_cases: WorkoutUseCases = Depends(get_workout_use_cases),
): ...
```

**When to fix:** When integration tests for endpoints become hard to set up, or when Container growth causes real ambiguity bugs.

---

## 🔐 Coding Constraints

- No business logic outside the domain layer
- No direct dependency from domain → infrastructure
- No global state
- No hidden side effects

---

## 🧪 Testing Strategy

- Use **pytest**
- Tests must be:
  - Isolated
  - Deterministic
- Use mocks for:
  - Repositories
  - External services

### Commands

- Run all tests:
  ```bash
  pytest