# API Design

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Liveness probe — always returns `{"status": "ok"}` |
| `GET` | `/ready` | Readiness probe — checks DB connectivity and model loaded |
| `POST` | `/search` | Semantic search (logs to `inference_requests`) |
| `GET` | `/documents/stats` | Chunk/document counts, model info |
| `GET` | `/inference/stats` | Inference request count, avg embedding/search latency |

## `POST /search`

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

## `GET /documents/stats`

**Response**:
```json
{
  "total_documents": 5,
  "total_chunks": 47,
  "embedding_dimension": 384,
  "model_name": "all-MiniLM-L6-v2"
}
```
