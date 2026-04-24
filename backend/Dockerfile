# ── Stage 1: builder ──────────────────────────────
FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml .
COPY src/ src/

RUN uv venv /app/.venv \
    && uv pip install --python /app/.venv/bin/python .

# ── Stage 2: runtime ─────────────────────────────
FROM python:3.12-slim

RUN useradd --create-home --uid 1000 appuser

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv

COPY alembic.ini .
COPY alembic/ alembic/
COPY entrypoint.sh .

ENV PATH="/app/.venv/bin:$PATH"

USER appuser

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
