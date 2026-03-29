# Epics and Issue Tracker

Development is tracked via 31 GitHub issues (RAG-001 to RAG-031) across 10 epics:

| Epic | Issues | Scope | Status |
|------|--------|-------|--------|
| 1. Infrastructure | RAG-001 — RAG-003 | Pre-commit, docker-compose, root justfile/README | Complete |
| 2. Shared Library | RAG-004 — RAG-008 | `lib-*`: scaffold, embedding client, DB/ORM, schemas, diagnostics | Complete |
| 3. Document Loader | RAG-009 — RAG-012 | `rag-loader`: scaffold, reader, chunker, App.run + sample docs | Complete |
| 4. Embedder | RAG-013 — RAG-015 | `rag-embedder`: scaffold, batch writer, App.run | Complete |
| 5. Retrieval API | RAG-016 — RAG-020 | `rag-retriever`: scaffold, health, /search, /stats, uvicorn | Complete |
| 6. Kubeflow Pipeline | RAG-021 — RAG-025 | `rag-pipeline`: scaffold, KFP components, pipeline def, Dockerfiles, Kind | Complete |
| 7. Integration | RAG-026 | End-to-end test | Complete |
| 8. Model Serving | RAG-028, RAG-030 | KServe Standard mode with HuggingFace runtime, remote embedding client | In progress |
| 9. Model Registry | RAG-029 | Kubeflow Model Registry deployment + Python SDK integration | In progress |
| 10. Observability | RAG-031 | Inference request logging table + stats endpoint | In progress |

Note: RAG-027 (custom model server package) was closed — replaced by KServe's built-in HuggingFace runtime.

## Implementation Order

```
Phase 1 (parallel):  RAG-001, RAG-002
Phase 2:             RAG-003, RAG-004
Phase 3 (parallel):  RAG-005, RAG-006, RAG-007, RAG-009, RAG-013, RAG-016, RAG-021
Phase 4 (parallel):  RAG-008, RAG-010, RAG-011, RAG-014, RAG-017, RAG-022
Phase 5 (parallel):  RAG-012, RAG-015, RAG-018, RAG-019, RAG-023
Phase 6:             RAG-020, RAG-024
Phase 7:             RAG-025, RAG-026
Phase 8:             RAG-028 (KServe infra)
Phase 9 (parallel):  RAG-029 (Model Registry), RAG-031 (inference table)
Phase 10:            RAG-030 (wire retriever to KServe)
```

## Future Enhancements (Out of Scope)

- PDF and HTML document support in `rag-loader`
- Reranking with a cross-encoder model
- Streaming responses from the retrieval API
- Multi-tenancy (multiple document collections)
- GitHub Actions CI pipeline
- Helm charts for production-like deployment
- LLM integration (generation step of RAG) — currently retrieval-only
- KServe autoscaling with KEDA
- `model-registry://` URI for KServe InferenceService storageUri
