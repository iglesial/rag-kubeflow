# Fluffy Cake Vector Store

Fluffy Cake includes a managed vector store built on PostgreSQL with pgvector. Users can create vector indexes through the dashboard or API without managing database infrastructure.

The vector store supports cosine similarity, Euclidean distance, and dot product searches. It uses IVFFlat indexing by default and switches to HNSW for collections exceeding one million vectors. Index tuning is automatic based on collection size.

Each Fluffy Cake workspace gets an isolated vector store with configurable dimensions (128, 384, 768, or 1536). Data is encrypted at rest and in transit. Backups run hourly with point-in-time recovery up to 7 days.
