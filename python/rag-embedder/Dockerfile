FROM python:3.13-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy lib dependencies first (better layer caching)
COPY python/lib-schemas/ python/lib-schemas/
COPY python/lib-embedding/ python/lib-embedding/
COPY python/lib-orm/ python/lib-orm/

# Copy the application package
COPY python/rag-embedder/ python/rag-embedder/

# Install production dependencies only
RUN cd python/rag-embedder && uv sync --no-dev --frozen

FROM python:3.13-slim

WORKDIR /app

# Copy the installed virtual environment from builder
COPY --from=builder /app/python/rag-embedder/.venv /app/python/rag-embedder/.venv
COPY --from=builder /app/python/rag-embedder/rag_embedder /app/python/rag-embedder/rag_embedder
COPY --from=builder /app/python/lib-schemas/lib_schemas /app/python/lib-schemas/lib_schemas
COPY --from=builder /app/python/lib-embedding/lib_embedding /app/python/lib-embedding/lib_embedding
COPY --from=builder /app/python/lib-orm/lib_orm /app/python/lib-orm/lib_orm

ENV PATH="/app/python/rag-embedder/.venv/bin:$PATH"

ENTRYPOINT ["python", "-m", "rag_embedder.main"]
