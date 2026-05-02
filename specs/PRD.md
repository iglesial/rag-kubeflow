# RAG Retrieval System — Product Requirements Document

> A locally-runnable RAG retrieval system for teaching MLOps to data engineering students, built with FastAPI, PostgreSQL+pgvector, and Kubeflow Pipelines.

## Problem

Data engineering students learning MLOps need a hands-on project that demonstrates real-world patterns — pipeline orchestration, vector databases, API serving, containerization — without requiring cloud accounts, paid APIs, or expensive hardware.

## Solution

A complete RAG (Retrieval-Augmented Generation) retrieval system that:
- Ingests documents, chunks them, and generates embeddings using a free local model
- Stores vectors in PostgreSQL with pgvector
- Serves a FastAPI semantic search API
- Orchestrates the ingestion pipeline through Kubeflow Pipelines on a local Kind cluster
- Serves the embedding model via KServe with an OpenAI-compatible endpoint
- Catalogs model versions in Kubeflow Model Registry
- Logs inference requests for observability

## Target Users

Data engineering students (intermediate Python, familiar with SQL, new to MLOps).

## Constraints

- Runs entirely on a student laptop (no cloud, no paid APIs, no GPU required)
- Uses only open-source, permissively-licensed components
- Prioritizes clarity and teachability over production optimization
- KFP 2.16.0+ required — older versions (2.3.0) used `gcr.io/ml-pipeline` images which Google has removed; 2.16.0 uses `ghcr.io` images and seaweedfs instead of minio

## Detailed Specifications

| Topic | File |
|-------|------|
| System architecture & data flow | [architecture.md](architecture.md) |
| Python packages & dependency graph | [packages.md](packages.md) |
| Embedding model, KServe & Model Registry | [embedding-model.md](embedding-model.md) |
| Database schema & inference logging | [database.md](database.md) |
| Retriever API endpoints | [api.md](api.md) |
| Infrastructure (Kind, KFP, KServe, docker-compose) | [infrastructure.md](infrastructure.md) |
| Epics, issues & implementation order | [epics.md](epics.md) |
| Key design decisions | [decisions.md](decisions.md) |
