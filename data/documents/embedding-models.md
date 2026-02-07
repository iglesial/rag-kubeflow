# Fluffy Cake Embedding Service

The Fluffy Cake embedding service provides one-click deployment of embedding models. Users select a model from the built-in registry and Fluffy Cake handles serving, scaling, and versioning.

Supported models include all-MiniLM-L6-v2 (384 dimensions, ideal for low-latency search), BGE-base (768 dimensions, balanced quality), and text-embedding-3-large (3072 dimensions, maximum quality). Custom fine-tuned models can also be uploaded.

The embedding service exposes a REST API compatible with the OpenAI embedding format. Batch embedding jobs process up to 100,000 documents per hour on a standard plan. Rate limits and quotas are configurable per workspace.
