# RAG Retrieval System — Product Requirements Document

> A locally-runnable RAG retrieval system for teaching MLOps to data engineering students, built with FastAPI, PostgreSQL+pgvector, and Kubeflow Pipelines.

---

## 1. Overview

### Problem

Data engineering students learning MLOps need a hands-on project that demonstrates real-world patterns — pipeline orchestration, vector databases, API serving, containerization — without requiring cloud accounts, paid APIs, or expensive hardware.

### Solution

A complete RAG (Retrieval-Augmented Generation) retrieval system that:
- Ingests documents, chunks them, and generates embeddings using a free local model
- Stores vectors in PostgreSQL with pgvector
- Serves a FastAPI semantic search API
- Orchestrates the ingestion pipeline through Kubeflow Pipelines on a local Kind cluster

### Target Users

Data engineering students (intermediate Python, familiar with SQL, new to MLOps).

### Constraints

- Runs entirely on a student laptop (no cloud, no paid APIs, no GPU required)
- Uses only open-source, permissively-licensed components
- Prioritizes clarity and teachability over production optimization

---

## 2. System Architecture

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

### Data Flow

1. **Load** — `rag-loader` reads `.md`/`.txt` files from disk, splits them into overlapping chunks using a recursive character splitter, outputs JSON
2. **Embed** — `rag-embedder` reads chunk JSON, generates 384-dim vectors via `all-MiniLM-L6-v2`, batch-inserts into pgvector with upsert
3. **Search** — `rag-retriever` accepts a query via `POST /search`, embeds it with the same model, performs cosine similarity search against pgvector, returns ranked results
4. **Orchestrate** — `rag-pipeline` defines a Kubeflow Pipeline that chains steps 1 and 2, running on a local Kind cluster

---

## 3. Python Packages

Five packages under `python/`, each following the `package-1` conventions (App class, projen-managed main.py, Pydantic BaseSettings task_inputs, justfile, pyproject.toml with uv).

### 3.1 `rag-shared` — Shared Library

Shared code used by embedder and retriever. Prevents duplication.

| Module | Contents |
|--------|----------|
| `settings.py` | `Settings` class: `db_url`, `embedding_model`, `vector_dim` |
| `db.py` | Async SQLAlchemy engine factory, async session generator |
| `models.py` | `DocumentChunk` ORM model (maps to `document_chunks` table) |
| `schemas.py` | Pydantic models: `ChunkInput`, `ChunkWithEmbedding`, `SearchRequest`, `SearchResult`, `SearchResponse`, `StatsResponse` |
| `embedding.py` | `EmbeddingClient` wrapping sentence-transformers: `encode()`, `dimension` |

**Dependencies**: `pydantic-settings`, `sqlalchemy[asyncio]`, `asyncpg`, `pgvector`, `sentence-transformers`

### 3.2 `rag-loader` — Document Loader

Reads documents from disk, chunks them, outputs JSON. Pure data processing — no DB or model dependency.

| Module | Contents |
|--------|----------|
| `reader.py` | `read_documents(input_dir)` — reads `.md`/`.txt` files, returns content + metadata |
| `chunker.py` | `chunk_text(text, chunk_size, chunk_overlap)` — recursive character splitter (from scratch, ~50 lines) |

**TaskInputs**: `input_dir`, `output_dir`, `chunk_size` (512), `chunk_overlap` (64)

Chunking strategy: recursive split on `["\n\n", "\n", ". ", " ", ""]`, no chunk exceeds `chunk_size`, consecutive chunks overlap by `chunk_overlap` characters.

### 3.3 `rag-embedder` — Embedding + Storage

Reads chunk JSON, generates embeddings, inserts into pgvector.

| Module | Contents |
|--------|----------|
| `writer.py` | `async write_chunks(session, chunks)` — batch upsert with `ON CONFLICT DO UPDATE` |

**TaskInputs**: `input_dir`, `db_url`, `embedding_model` (`all-MiniLM-L6-v2`), `batch_size` (32)

### 3.4 `rag-retriever` — FastAPI Retrieval Service

Semantic search API.

| Module | Contents |
|--------|----------|
| `api.py` | `create_app()` — FastAPI application factory |
| `dependencies.py` | DI for async DB session + embedding client |
| `routes/health.py` | `GET /health`, `GET /ready` |
| `routes/search.py` | `POST /search` |
| `routes/documents.py` | `GET /documents/stats` |

**TaskInputs**: `host` (`0.0.0.0`), `port` (8000), `db_url`, `embedding_model`, `top_k` (5)

### 3.5 `rag-pipeline` — Kubeflow Pipeline

Defines and submits the ingestion pipeline to KFP.

| Module | Contents |
|--------|----------|
| `components/loader.py` | `@dsl.component` wrapping rag-loader container image |
| `components/embedder.py` | `@dsl.component` wrapping rag-embedder container image |
| `pipeline.py` | `@dsl.pipeline` chaining loader -> embedder via artifact passing |

**TaskInputs**: `pipeline_name`, `input_dir`, `kubeflow_host`, `compile_only` (bool)

### Dependency Graph

```
rag-shared         (no internal deps)
  ^
  ├── rag-loader   (schemas only)
  ├── rag-embedder (schemas, DB, embedding client)
  └── rag-retriever(schemas, DB, embedding client)

rag-pipeline       (references loader + embedder as container images)
```

---

## 4. Embedding Model

**`sentence-transformers/all-MiniLM-L6-v2`**

| Property | Value |
|----------|-------|
| Dimensions | 384 |
| Model size | ~80 MB |
| Speed | ~14,000 sentences/sec on CPU |
| License | Apache 2.0 |
| API key required | No |
| GPU required | No |

Chosen because it runs fast on CPU, requires no API key, downloads automatically on first use (~80 MB to `~/.cache/huggingface/`), and produces good quality embeddings for its size.

Configurable via `task_inputs.embedding_model` for alternatives like `paraphrase-MiniLM-L3-v2` (128-dim, smaller) on constrained hardware.

---

## 5. Database Design

### PostgreSQL 16 + pgvector

Running via docker-compose. Connection: `postgresql+asyncpg://rag:rag@localhost:5432/rag`.

### Schema

```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE document_chunks (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_name VARCHAR(512) NOT NULL,
    chunk_index   INTEGER NOT NULL,
    content       TEXT NOT NULL,
    metadata      JSONB NOT NULL DEFAULT '{}',
    embedding     vector(384) NOT NULL,
    created_at    TIMESTAMP WITH TIME ZONE DEFAULT now(),

    CONSTRAINT uq_document_chunk UNIQUE (document_name, chunk_index)
);
```

### Indexes

```sql
-- Approximate nearest neighbor (IVFFlat, cosine distance)
CREATE INDEX idx_chunks_embedding ON document_chunks
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Filter by document name
CREATE INDEX idx_chunks_document_name ON document_chunks (document_name);
```

### Search Query

```sql
SELECT id, document_name, content, metadata,
       1 - (embedding <=> :query_embedding) AS similarity_score
FROM document_chunks
WHERE 1 - (embedding <=> :query_embedding) >= :threshold
ORDER BY embedding <=> :query_embedding
LIMIT :top_k;
```

`<=>` is pgvector's cosine distance operator. `1 - distance = similarity`.

---

## 6. API Design

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Liveness probe — always returns `{"status": "ok"}` |
| `GET` | `/ready` | Readiness probe — checks DB connectivity and model loaded |
| `POST` | `/search` | Semantic search |
| `GET` | `/documents/stats` | Chunk/document counts, model info |

### `POST /search`

**Request**:
```json
{
  "query": "what is continuous integration for ML?",
  "top_k": 5,
  "similarity_threshold": 0.3
}
```

| Field | Type | Default | Validation |
|-------|------|---------|------------|
| `query` | string | required | min_length=1, max_length=1000 |
| `top_k` | int | 5 | ge=1, le=50 |
| `similarity_threshold` | float | 0.0 | ge=0.0, le=1.0 |

**Response**:
```json
{
  "query": "what is continuous integration for ML?",
  "results": [
    {
      "chunk_id": "550e8400-...",
      "document_name": "02-cicd-for-ml.md",
      "content": "Continuous integration for ML extends...",
      "similarity_score": 0.82,
      "metadata": {"extension": ".md", "file_size": 4096}
    }
  ],
  "total_results": 1,
  "embedding_time_ms": 12.3,
  "search_time_ms": 4.7
}
```

### `GET /documents/stats`

**Response**:
```json
{
  "total_documents": 5,
  "total_chunks": 47,
  "embedding_dimension": 384,
  "model_name": "all-MiniLM-L6-v2"
}
```

---

## 7. Infrastructure

### Local Services (docker-compose)

| Service | Image | Port | Purpose |
|---------|-------|------|---------|
| postgres | `pgvector/pgvector:pg16` | 5432 | Vector database |

Credentials: `rag` / `rag` / `rag` (user/password/database).

### Kubeflow Pipelines (Kind)

Students set up a local Kubernetes cluster from day one:

1. `kind create cluster --name rag-kubeflow` — single-node K8s cluster in Docker
2. Deploy KFP standalone manifests via `kubectl apply -k`
3. Port-forward the UI: `kubectl port-forward svc/ml-pipeline-ui -n kubeflow 8080:80`
4. Load component images: `kind load docker-image rag-loader:latest --name rag-kubeflow`

### Container Images

Each runnable package gets a Dockerfile: Python 3.13-slim base, uv for dependency installation, copies `rag-shared` as a dependency, entrypoint is the `main` script.

| Image | Source | Used by |
|-------|--------|---------|
| `rag-loader:latest` | `python/rag-loader/Dockerfile` | KFP loader component |
| `rag-embedder:latest` | `python/rag-embedder/Dockerfile` | KFP embedder component |
| `rag-retriever:latest` | `python/rag-retriever/Dockerfile` | Standalone API service |

---

## 8. Code Quality

| Tool | Config | Purpose |
|------|--------|---------|
| Ruff | line-length=100, py313, rules E/W/F/I/B/C4/UP/D, numpy pydoc | Lint + format |
| Mypy | strict=true | Type checking |
| Pytest | --strict-markers, --strict-config, --cov | Testing + coverage |
| Pre-commit | ruff + mypy + standard hooks | Gate on every commit |
| uv | Lock files committed | Reproducible installs |
| Just | justfile per package + root orchestrator | Task runner |

---

## 9. Sample Data

`data/documents/` ships with 3-5 markdown files on MLOps topics:
- What is MLOps?
- CI/CD for Machine Learning
- Feature Stores Introduction
- Model Monitoring and Observability
- Vector Databases and Embeddings

These give students immediate, meaningful search results without needing to bring their own data.

---

## 10. Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| 5 packages instead of monolith | Teaches separation of concerns; each is a deployable unit; mirrors real microservice patterns |
| `rag-shared` as library | Prevents duplication of DB models, schemas, embedding client between embedder and retriever |
| Recursive character splitter from scratch | Teaches chunking internals (~50 lines) instead of hiding them behind LangChain |
| `all-MiniLM-L6-v2` | 80 MB, CPU-fast, no API key, Apache 2.0, 384 dims — sweet spot for student laptops |
| pgvector over Chroma/Pinecone | Teaches real SQL + vector concepts without a separate service; PostgreSQL is a skill students already have |
| Async SQLAlchemy + asyncpg | Matches FastAPI's async model; teaches modern Python async patterns |
| Kind from day one | Students learn real Kubernetes from the start, not a shortcut that hides the orchestration layer |
| JSON artifacts between loader and embedder | Clean separation; inspectable intermediate output; maps to Kubeflow artifact passing |
| Projen-managed main.py | Consistent entry point pattern across all packages; students never edit it |
| Per-package justfile + root orchestrator | Each package works independently; root justfile ties them together |

---

## 11. Epics and Issue Tracker

Development is tracked via 26 GitHub issues (RAG-001 to RAG-026) across 7 epics:

| Epic | Issues | Scope |
|------|--------|-------|
| 1. Infrastructure | RAG-001 — RAG-003 | Pre-commit, docker-compose, root justfile/README |
| 2. Shared Library | RAG-004 — RAG-008 | `rag-shared`: scaffold, embedding client, DB/ORM, schemas, diagnostics |
| 3. Document Loader | RAG-009 — RAG-012 | `rag-loader`: scaffold, reader, chunker, App.run + sample docs |
| 4. Embedder | RAG-013 — RAG-015 | `rag-embedder`: scaffold, batch writer, App.run |
| 5. Retrieval API | RAG-016 — RAG-020 | `rag-retriever`: scaffold, health, /search, /stats, uvicorn |
| 6. Kubeflow Pipeline | RAG-021 — RAG-025 | `rag-pipeline`: scaffold, KFP components, pipeline def, Dockerfiles, Kind |
| 7. Integration | RAG-026 | End-to-end test |

### Implementation Order

```
Phase 1 (parallel):  RAG-001, RAG-002
Phase 2:             RAG-003, RAG-004
Phase 3 (parallel):  RAG-005, RAG-006, RAG-007, RAG-009, RAG-013, RAG-016, RAG-021
Phase 4 (parallel):  RAG-008, RAG-010, RAG-011, RAG-014, RAG-017, RAG-022
Phase 5 (parallel):  RAG-012, RAG-015, RAG-018, RAG-019, RAG-023
Phase 6:             RAG-020, RAG-024
Phase 7:             RAG-025, RAG-026
```

---

## 12. Final Repository Structure

```
rag-kubeflow/
├── CLAUDE.md
├── .pre-commit-config.yaml
├── docker-compose.yml
├── justfile
├── README.md
├── specs/
│   └── PRD.md                  (this file)
├── infra/
│   ├── init.sql                (pgvector schema)
│   ├── kind-config.yaml
│   └── setup-kubeflow.sh
├── data/
│   └── documents/              (sample MLOps markdown files)
├── python/
│   ├── package-1/              (template/example)
│   ├── rag-shared/
│   ├── rag-loader/
│   ├── rag-embedder/
│   ├── rag-retriever/
│   └── rag-pipeline/
└── tests/
    └── e2e/
        └── test_full_pipeline.py
```

---

## 13. Future Enhancements (Out of Scope)

- PDF and HTML document support in `rag-loader`
- Reranking with a cross-encoder model
- Streaming responses from the retrieval API
- Multi-tenancy (multiple document collections)
- GitHub Actions CI pipeline
- Helm charts for production-like deployment
- LLM integration (generation step of RAG) — currently retrieval-only
