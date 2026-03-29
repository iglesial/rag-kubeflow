# Python Packages

Five packages + three shared libraries under `python/`, each following the `package-1` conventions (App class, projen-managed main.py, Pydantic BaseSettings task_inputs, justfile, pyproject.toml with uv).

## Shared Libraries (`lib-embedding`, `lib-orm`, `lib-schemas`)

Three shared libraries used by embedder and retriever. Prevents duplication.

| Package | Module | Contents |
|---------|--------|----------|
| `lib-embedding` | `embedding.py` | `EmbeddingClient` wrapping sentence-transformers: `encode()`, `dimension` |
| `lib-embedding` | `remote.py` | `RemoteEmbeddingClient` — HTTP client for KServe OpenAI-compatible endpoint |
| `lib-orm` | `db.py` | Async SQLAlchemy engine factory, async session generator |
| `lib-orm` | `models.py` | `DocumentChunk` + `InferenceRequest` ORM models |
| `lib-schemas` | `schemas.py` | Pydantic models: `ChunkInput`, `ChunkWithEmbedding`, `SearchRequest`, `SearchResult`, `SearchResponse`, `StatsResponse`, `InferenceStatsResponse` |

**Dependencies**: `pydantic-settings`, `sqlalchemy[asyncio]`, `asyncpg`, `pgvector`, `sentence-transformers`, `httpx`

## `rag-loader` — Document Loader

Reads documents from disk, chunks them, outputs JSON. Pure data processing — no DB or model dependency.

| Module | Contents |
|--------|----------|
| `reader.py` | `read_documents(input_dir)` — reads `.md`/`.txt` files, returns content + metadata |
| `chunker.py` | `chunk_text(text, chunk_size, chunk_overlap)` — recursive character splitter (from scratch, ~50 lines) |

**TaskInputs**: `input_dir`, `output_dir`, `chunk_size` (512), `chunk_overlap` (64)

Chunking strategy: recursive split on `["\n\n", "\n", ". ", " ", ""]`, no chunk exceeds `chunk_size`, consecutive chunks overlap by `chunk_overlap` characters.

## `rag-embedder` — Embedding + Storage

Reads chunk JSON, generates embeddings, inserts into pgvector.

| Module | Contents |
|--------|----------|
| `writer.py` | `async write_chunks(session, chunks)` — batch upsert with `ON CONFLICT DO UPDATE` |

**TaskInputs**: `input_dir`, `db_url`, `embedding_model` (`all-MiniLM-L6-v2`), `batch_size` (32)

## `rag-retriever` — FastAPI Retrieval Service

Semantic search API. Supports both local embedding (in-process) and remote embedding via KServe.

| Module | Contents |
|--------|----------|
| `api.py` | `create_app()` — FastAPI application factory |
| `dependencies.py` | DI for async DB session + embedding client (local or remote) |
| `routes/health.py` | `GET /health`, `GET /ready` |
| `routes/search.py` | `POST /search` — logs inference requests to `inference_requests` table |
| `routes/documents.py` | `GET /documents/stats`, `GET /inference/stats` |

**TaskInputs**: `host` (`0.0.0.0`), `port` (8000), `db_url`, `embedding_model`, `top_k` (5), `embedding_endpoint` (optional, URL of KServe service)

## `rag-pipeline` — Kubeflow Pipeline

Defines and submits the ingestion pipeline to KFP.

| Module | Contents |
|--------|----------|
| `components/loader.py` | `@dsl.container_component` wrapping rag-loader container image |
| `components/embedder.py` | `@dsl.container_component` wrapping rag-embedder container image |
| `pipeline.py` | `@dsl.pipeline` chaining loader -> embedder via artifact passing |

**TaskInputs**: `pipeline_name`, `input_dir`, `kubeflow_host`, `compile_only` (bool)

## Dependency Graph

```
lib-embedding      (sentence-transformers, httpx)
lib-orm            (sqlalchemy, asyncpg, pgvector)
lib-schemas        (pydantic)
  ^
  ├── rag-loader   (lib-schemas only)
  ├── rag-embedder (lib-schemas, lib-orm, lib-embedding)
  └── rag-retriever(lib-schemas, lib-orm, lib-embedding)

rag-pipeline       (references loader + embedder as container images)
```
