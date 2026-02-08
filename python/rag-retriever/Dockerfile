FROM python:3.13-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy lib dependencies first (better layer caching)
COPY python/lib-schemas/ python/lib-schemas/
COPY python/lib-embedding/ python/lib-embedding/
COPY python/lib-orm/ python/lib-orm/

# Copy the application package
COPY python/rag-retriever/ python/rag-retriever/

# Install production dependencies only
RUN cd python/rag-retriever && uv sync --no-dev --frozen

FROM python:3.13-slim

WORKDIR /app

# Copy the installed virtual environment from builder
COPY --from=builder /app/python/rag-retriever/.venv /app/python/rag-retriever/.venv
COPY --from=builder /app/python/rag-retriever/rag_retriever /app/python/rag-retriever/rag_retriever
COPY --from=builder /app/python/lib-schemas/lib_schemas /app/python/lib-schemas/lib_schemas
COPY --from=builder /app/python/lib-embedding/lib_embedding /app/python/lib-embedding/lib_embedding
COPY --from=builder /app/python/lib-orm/lib_orm /app/python/lib-orm/lib_orm

ENV PATH="/app/python/rag-retriever/.venv/bin:$PATH"

EXPOSE 8000

ENTRYPOINT ["python", "-m", "rag_retriever.main"]
