FROM python:3.13-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy lib dependencies first (better layer caching)
COPY python/lib-schemas/ python/lib-schemas/

# Copy the application package
COPY python/rag-loader/ python/rag-loader/

# Install production dependencies only
RUN cd python/rag-loader && uv sync --no-dev --frozen

FROM python:3.13-slim

WORKDIR /app

# Copy the installed virtual environment from builder
COPY --from=builder /app/python/rag-loader/.venv /app/python/rag-loader/.venv
COPY --from=builder /app/python/rag-loader/rag_loader /app/python/rag-loader/rag_loader
COPY --from=builder /app/python/lib-schemas/lib_schemas /app/python/lib-schemas/lib_schemas

# Copy sample documents for local Kind deployment
COPY data/documents/ /data/documents/

ENV PATH="/app/python/rag-loader/.venv/bin:$PATH"

ENTRYPOINT ["python", "-m", "rag_loader.main"]
