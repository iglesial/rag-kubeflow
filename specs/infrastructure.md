# Infrastructure

## Local Services (docker-compose)

| Service | Image | Port | Purpose |
|---------|-------|------|---------|
| postgres | `pgvector/pgvector:pg16` | 5432 | Vector database |

Credentials: `rag` / `rag` / `rag` (user/password/database).

## Kubeflow Pipelines (Kind)

Students set up a local Kubernetes cluster from day one:

1. `kind create cluster --name rag-kubeflow` — single-node K8s cluster in Docker
2. Deploy KFP standalone manifests via `kubectl apply -k`
3. Port-forward the UI: `kubectl port-forward svc/ml-pipeline-ui -n kubeflow 8080:80`
4. Load component images: `kind load docker-image rag-loader:local --name rag-kubeflow`

## KServe (Kind)

KServe Standard mode (no Knative) for model serving:

1. Install cert-manager (>= 1.15.0) for webhook TLS certs
2. Install Gateway API CRDs
3. Install KServe via Helm with `deploymentMode=Standard`
4. Apply InferenceService YAML — HuggingFace runtime auto-downloads model from HF Hub

## Kubeflow Model Registry (Kind)

Standalone Model Registry (v0.3.5) deployed via kustomize alongside KFP:

```bash
kubectl apply -n kubeflow -k "https://github.com/kubeflow/model-registry/manifests/kustomize/overlays/db?ref=v0.3.5"
```

## Container Images

Each runnable package gets a Dockerfile: Python 3.13-slim base, uv for dependency installation, copies shared libs as dependencies, entrypoint is the `main` script.

| Image | Source | Used by |
|-------|--------|---------|
| `rag-loader:local` | `python/rag-loader/Dockerfile` | KFP loader component |
| `rag-embedder:local` | `python/rag-embedder/Dockerfile` | KFP embedder component |
| `rag-retriever:local` | `python/rag-retriever/Dockerfile` | Standalone API service |

## Code Quality

| Tool | Config | Purpose |
|------|--------|---------|
| Ruff | line-length=100, py313, rules E/W/F/I/B/C4/UP/D, numpy pydoc | Lint + format |
| Mypy | strict=true | Type checking |
| Pytest | --strict-markers, --strict-config, --cov | Testing + coverage |
| Pre-commit | ruff + mypy + standard hooks | Gate on every commit |
| uv | Lock files committed | Reproducible installs |
| Just | justfile per package + root orchestrator | Task runner |

## Sample Data

`data/documents/` ships with 3-5 markdown files on MLOps topics:
- What is MLOps?
- CI/CD for Machine Learning
- Feature Stores Introduction
- Model Monitoring and Observability
- Vector Databases and Embeddings

These give students immediate, meaningful search results without needing to bring their own data.

## Repository Structure

```
rag-kubeflow/
├── CLAUDE.md
├── .pre-commit-config.yaml
├── docker-compose.yml
├── justfile
├── README.md
├── specs/
│   ├── PRD.md
│   ├── architecture.md
│   ├── packages.md
│   ├── embedding-model.md
│   ├── database.md
│   ├── api.md
│   ├── infrastructure.md
│   ├── epics.md
│   └── decisions.md
├── infra/
│   ├── init.sql                (pgvector schema + inference_requests table)
│   ├── kind-config.yaml
│   └── kserve/
│       └── inference-service.yaml  (KServe InferenceService for embedding model)
├── data/
│   └── documents/              (sample MLOps markdown files)
├── python/
│   ├── package-1/              (template/example)
│   ├── lib-embedding/          (local + remote embedding clients)
│   ├── lib-orm/                (async SQLAlchemy + pgvector ORM models)
│   ├── lib-schemas/            (shared Pydantic schemas)
│   ├── rag-loader/
│   ├── rag-embedder/
│   ├── rag-retriever/
│   └── rag-pipeline/
└── tests/
    └── e2e/
        └── test_full_pipeline.py
```
