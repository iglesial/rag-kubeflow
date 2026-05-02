# Database Design

## PostgreSQL 16 + pgvector

Running via docker-compose. Connection: `postgresql+asyncpg://rag:rag@localhost:5432/rag`.

## Schema

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

## Indexes

```sql
-- Approximate nearest neighbor (IVFFlat, cosine distance)
CREATE INDEX idx_chunks_embedding ON document_chunks
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Filter by document name
CREATE INDEX idx_chunks_document_name ON document_chunks (document_name);
```

## Search Query

```sql
SELECT id, document_name, content, metadata,
       1 - (embedding <=> :query_embedding) AS similarity_score
FROM document_chunks
WHERE 1 - (embedding <=> :query_embedding) >= :threshold
ORDER BY embedding <=> :query_embedding
LIMIT :top_k;
```

`<=>` is pgvector's cosine distance operator. `1 - distance = similarity`.

## Inference Logging Table

```sql
CREATE TABLE inference_requests (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    query         TEXT NOT NULL,
    model_name    VARCHAR(256) NOT NULL,
    model_version VARCHAR(128),
    embedding_ms  FLOAT NOT NULL,
    search_ms     FLOAT NOT NULL,
    result_count  INT NOT NULL,
    top_score     FLOAT,
    created_at    TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE INDEX idx_inference_created ON inference_requests (created_at DESC);
```

Every query-time `/search` request inserts a row (async, non-blocking). Batch embedding during pipeline ingestion is NOT logged.
