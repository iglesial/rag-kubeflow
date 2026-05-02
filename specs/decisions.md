# Key Design Decisions

## Original Decisions (Epics 1-7)

| Decision | Rationale |
|----------|-----------|
| 5 packages instead of monolith | Teaches separation of concerns; each is a deployable unit; mirrors real microservice patterns |
| Shared libraries (`lib-*`) | Prevents duplication of DB models, schemas, embedding client between embedder and retriever |
| Recursive character splitter from scratch | Teaches chunking internals (~50 lines) instead of hiding them behind LangChain |
| `all-MiniLM-L6-v2` | 80 MB, CPU-fast, no API key, Apache 2.0, 384 dims — sweet spot for student laptops |
| pgvector over Chroma/Pinecone | Teaches real SQL + vector concepts without a separate service; PostgreSQL is a skill students already have |
| Async SQLAlchemy + asyncpg | Matches FastAPI's async model; teaches modern Python async patterns |
| Kind from day one | Students learn real Kubernetes from the start, not a shortcut that hides the orchestration layer |
| KFP 2.16.0 over 2.3.0 | Google removed all `gcr.io/ml-pipeline` images; 2.16.0 uses `ghcr.io` registry and seaweedfs instead of minio |
| JSON artifacts between loader and embedder | Clean separation; inspectable intermediate output; maps to Kubeflow artifact passing |
| Projen-managed main.py | Consistent entry point pattern across all packages; students never edit it |
| Per-package justfile + root orchestrator | Each package works independently; root justfile ties them together |

## Model Serving Decisions (Epics 8-10)

| Decision | Rationale |
|----------|-----------|
| KServe built-in HuggingFace runtime over custom model server | No custom code needed; KServe natively supports `text_embedding` task with `--backend=huggingface` |
| KServe Standard mode (no Knative) | Simpler infra for Kind; regular Deployments + Services |
| OpenAI-compatible embedding endpoint | Standard API format; easy to swap models; `httpx` client is straightforward |
| Local fallback when KServe not configured | Backward compatibility; e2e tests keep working without full infra |
| Inference logging as async fire-and-forget | Search response time not affected by DB write |
| Model Registry alongside KFP | Central source of truth for model versions; future `model-registry://` URI support |
