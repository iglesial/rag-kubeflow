# System Architecture

## Current Architecture (Epics 1-7, complete)

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

## Target Architecture (Epics 8-10, in progress)

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
                  ┌─────────────────┐       v
                  │ Model Registry  │  ┌───────────────────┐
                  │  (v0.3.5)       │  │ PostgreSQL+pgvector│
                  │  catalogs model │  │  document_chunks   │
                  │  versions       │  │  inference_requests│
                  └─────────────────┘  └─────────┬─────────┘
                                                 │ cosine search
                                                 v
                               ┌───────────────────────────┐
                               │     rag-retriever          │
                               │   (FastAPI on :8000)       │
                               │   POST /search             │
                               │   GET /inference/stats     │
                               └────────────┬──────────────┘
                                            │ HTTP (OpenAI-compat)
                                            v
                               ┌───────────────────────────┐
                               │   KServe InferenceService  │
                               │   HuggingFace runtime      │
                               │   all-MiniLM-L6-v2         │
                               │   /openai/v1/embeddings    │
                               └───────────────────────────┘
```

Key changes in target architecture:
1. **KServe** serves the embedding model standalone (no custom server, uses built-in HF runtime)
2. **Model Registry** catalogs model versions for both batch pipeline and KServe
3. **Retriever** calls KServe via HTTP instead of loading model in-process (with local fallback)
4. **Inference table** logs every query-time embedding + search request

## Data Flow

1. **Load** — `rag-loader` reads `.md`/`.txt` files from disk, splits them into overlapping chunks using a recursive character splitter, outputs JSON
2. **Embed** — `rag-embedder` reads chunk JSON, generates 384-dim vectors via `all-MiniLM-L6-v2`, batch-inserts into pgvector with upsert
3. **Search** — `rag-retriever` accepts a query via `POST /search`, calls KServe for embeddings (or falls back to local model), performs cosine similarity search against pgvector, returns ranked results
4. **Orchestrate** — `rag-pipeline` defines a Kubeflow Pipeline that chains steps 1 and 2, running on a local Kind cluster
5. **Serve Model** — KServe InferenceService serves `all-MiniLM-L6-v2` via built-in HuggingFace runtime, exposing an OpenAI-compatible `/openai/v1/embeddings` endpoint
6. **Catalog** — Kubeflow Model Registry tracks model versions, referenced by both the batch pipeline and KServe
7. **Observe** — Every query-time search request is logged to `inference_requests` table for monitoring
