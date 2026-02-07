# RAG Kubeflow

A locally-runnable RAG retrieval system for teaching MLOps to data engineering students, built with FastAPI, PostgreSQL+pgvector, and Kubeflow Pipelines.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│              Kubeflow Pipeline (Kind cluster)            │
│                                                         │
│  ┌──────────────┐   JSON chunks   ┌────────────────┐   │
│  │  rag-loader   │───────────────>│  rag-embedder   │   │
│  │  (chunk docs) │   (artifact)   │  (embed+store)  │   │
│  └──────────────┘                 └───────┬────────┘   │
│                                           │            │
└───────────────────────────────────────────┼────────────┘
                                            │ writes vectors
                                            v
                               ┌───────────────────┐
                               │ PostgreSQL+pgvector│
                               │   (docker-compose) │
                               └─────────┬─────────┘
                                         │ cosine search
                                         v
                               ┌───────────────────┐
                               │   rag-retriever    │
                               │ (FastAPI on :8000) │
                               └───────────────────┘
```

## Prerequisites

- **Python 3.13+**
- **[uv](https://docs.astral.sh/uv/)** — Python package manager
- **[Docker](https://docs.docker.com/get-docker/)** — for PostgreSQL and container images
- **[just](https://github.com/casey/just)** — task runner
- **[pre-commit](https://pre-commit.com/)** — git hooks
- **[Kind](https://kind.sigs.k8s.io/)** — local Kubernetes cluster
- **[kubectl](https://kubernetes.io/docs/tasks/tools/)** — Kubernetes CLI

## First-Time Setup

```bash
# 1. Clone the repository
git clone https://github.com/iglesial/rag-kubeflow.git
cd rag-kubeflow

# 2. Install pre-commit hooks
pre-commit install

# 3. Start PostgreSQL
just infra-up

# 4. Install all Python packages
just install-all
```

## Daily Workflow

```bash
# Start infrastructure
just infra-up

# Run all checks (lint + format + typecheck)
just check-all

# Run all tests
just test-all

# Stop infrastructure when done
just infra-down
```

## Available Commands

Run `just --list` at the repo root to see all commands:

| Command | Description |
|---------|-------------|
| `just infra-up` | Start PostgreSQL via docker-compose |
| `just infra-down` | Stop PostgreSQL |
| `just infra-status` | Show infrastructure status |
| `just install-all` | Install all packages (dev dependencies) |
| `just check-all` | Run lint + format check + typecheck across all packages |
| `just test-all` | Run tests across all packages |
| `just pre-commit` | Run pre-commit hooks on all files |

Each package under `python/` has its own `justfile` with package-specific commands. Run `just --list` inside any package directory.

## Packages

| Package | Description |
|---------|-------------|
| `python/lib-embedding` | Embedding client library (sentence-transformers) |
| `python/lib-orm` | Database connection and ORM model (async SQLAlchemy + pgvector) |
| `python/rag-loader` | Read documents, chunk them, output JSON |
| `python/rag-embedder` | Embed chunks (batch), insert into pgvector |
| `python/rag-retriever` | FastAPI semantic search API |
| `python/rag-pipeline` | Kubeflow Pipeline definition |

## Infrastructure

### PostgreSQL + pgvector

```bash
just infra-up    # Starts on localhost:5432
just infra-down  # Stops the container
```

Credentials: `rag` / `rag` / `rag` (user / password / database).

Connection string: `postgresql+asyncpg://rag:rag@localhost:5432/rag`
