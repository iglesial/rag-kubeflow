# Root justfile for rag-kubeflow
# Run `just --list` to see all available commands

set shell := ["powershell", "-NoProfile", "-Command"]

# KFP manifest version for standalone deployment
KFP_VERSION := "2.16.0"
# Kind cluster name
KIND_CLUSTER := "rag-kubeflow"

# Default recipe to display help
default:
    @just --list

# --- Infrastructure ---

# Start Docker Desktop (waits until daemon is ready)
docker-start:
    @if (-not (Get-Process "Docker Desktop" -ErrorAction SilentlyContinue)) { \
        Write-Host "Starting Docker Desktop..." -ForegroundColor Cyan; \
        Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"; \
    } else { \
        Write-Host "Docker Desktop already running." -ForegroundColor Green; \
    }
    @Write-Host "Waiting for Docker daemon..." -ForegroundColor Yellow
    @while (-not (docker info 2>$null)) { Start-Sleep -Seconds 2 }
    @Write-Host "Docker is ready." -ForegroundColor Green

# Start all infrastructure: PostgreSQL, Kind cluster, KFP, load images
infra-up: docker-start
    @Write-Host "Starting PostgreSQL..." -ForegroundColor Cyan
    docker compose up -d
    @Write-Host "Creating Kind cluster '{{KIND_CLUSTER}}'..." -ForegroundColor Cyan
    kind create cluster --name {{KIND_CLUSTER}} --config infra/kind-config.yaml --wait 60s
    @Write-Host "Deploying KFP cluster-scoped resources ({{KFP_VERSION}})..." -ForegroundColor Cyan
    kubectl apply -k "github.com/kubeflow/pipelines/manifests/kustomize/cluster-scoped-resources?ref={{KFP_VERSION}}"
    kubectl wait crd/applications.app.k8s.io --for condition=established --timeout=60s
    @Write-Host "Deploying KFP platform-agnostic environment..." -ForegroundColor Cyan
    kubectl apply -k "github.com/kubeflow/pipelines/manifests/kustomize/env/platform-agnostic?ref={{KFP_VERSION}}"
    @Write-Host "Waiting for KFP pods to be ready (this may take several minutes)..." -ForegroundColor Cyan
    kubectl wait pods -l application-crd-id=kubeflow-pipelines -n kubeflow --for condition=Ready --timeout=1800s
    @Write-Host "Loading pipeline images into Kind..." -ForegroundColor Cyan
    kind load docker-image rag-loader:local --name {{KIND_CLUSTER}}
    kind load docker-image rag-embedder:local --name {{KIND_CLUSTER}}
    @Write-Host "Infrastructure ready! Run 'just kfp-ui' for KFP, 'just serve' for retriever." -ForegroundColor Green

# Stop all infrastructure: PostgreSQL + Kind cluster
infra-down:
    @Write-Host "Deleting Kind cluster '{{KIND_CLUSTER}}'..." -ForegroundColor Cyan
    -kind delete cluster --name {{KIND_CLUSTER}}
    @Write-Host "Stopping PostgreSQL..." -ForegroundColor Cyan
    docker compose down

# Show infrastructure status (PostgreSQL + KFP pods)
infra-status:
    @Write-Host "=== PostgreSQL ===" -ForegroundColor Cyan
    docker compose ps
    @Write-Host ""
    @Write-Host "=== KFP Pods ===" -ForegroundColor Cyan
    -kubectl get pods -n kubeflow

# --- Kubeflow Pipelines ---

# Create Kind cluster and deploy KFP standalone
kfp-setup:
    @Write-Host "Creating Kind cluster '{{KIND_CLUSTER}}'..." -ForegroundColor Cyan
    kind create cluster --name {{KIND_CLUSTER}} --config infra/kind-config.yaml --wait 60s
    @Write-Host "Deploying KFP cluster-scoped resources ({{KFP_VERSION}})..." -ForegroundColor Cyan
    kubectl apply -k "github.com/kubeflow/pipelines/manifests/kustomize/cluster-scoped-resources?ref={{KFP_VERSION}}"
    kubectl wait crd/applications.app.k8s.io --for condition=established --timeout=60s
    @Write-Host "Deploying KFP platform-agnostic environment..." -ForegroundColor Cyan
    kubectl apply -k "github.com/kubeflow/pipelines/manifests/kustomize/env/platform-agnostic?ref={{KFP_VERSION}}"
    @Write-Host "Waiting for KFP pods to be ready (this may take several minutes)..." -ForegroundColor Cyan
    kubectl wait pods -l application-crd-id=kubeflow-pipelines -n kubeflow --for condition=Ready --timeout=600s
    @Write-Host "KFP deployed successfully! Run 'just kfp-ui' to access the UI." -ForegroundColor Green

# Port-forward KFP UI to localhost:8080
kfp-ui:
    @Write-Host "Forwarding KFP UI to http://localhost:8080 ..." -ForegroundColor Cyan
    @Write-Host "Press Ctrl+C to stop." -ForegroundColor Yellow
    kubectl port-forward -n kubeflow svc/ml-pipeline-ui 8080:80

# Load pipeline Docker images into Kind cluster
kfp-load-images:
    @Write-Host "Loading Docker images into Kind cluster '{{KIND_CLUSTER}}'..." -ForegroundColor Cyan
    kind load docker-image rag-loader:local --name {{KIND_CLUSTER}}
    kind load docker-image rag-embedder:local --name {{KIND_CLUSTER}}
    @Write-Host "Images loaded successfully." -ForegroundColor Green

# Delete the Kind cluster
kfp-teardown:
    @Write-Host "Deleting Kind cluster '{{KIND_CLUSTER}}'..." -ForegroundColor Cyan
    kind delete cluster --name {{KIND_CLUSTER}}
    @Write-Host "Cluster deleted." -ForegroundColor Green

# Show KFP pod status
kfp-status:
    kubectl get pods -n kubeflow

# --- Docker ---

# Build all Docker images
build-images:
    docker build -t rag-loader:latest -t rag-loader:local -f python/rag-loader/Dockerfile .
    docker build -t rag-embedder:latest -t rag-embedder:local -f python/rag-embedder/Dockerfile .
    docker build -t rag-retriever:latest -f python/rag-retriever/Dockerfile .

# --- RAG Pipeline (local) ---

# Run the loader (chunk documents → JSON)
load:
    @Write-Host "Running rag-loader..." -ForegroundColor Cyan
    Push-Location python/rag-loader; uv run main --input-dir ../../data/documents; Pop-Location

# Run the embedder (embed chunks → pgvector)
embed:
    @Write-Host "Running rag-embedder..." -ForegroundColor Cyan
    Push-Location python/rag-embedder; uv run main; Pop-Location

# Run the full local pipeline: loader then embedder
pipeline: load embed

# Submit the pipeline to KFP (requires 'just kfp-ui' running in another terminal)
kfp-submit:
    @Write-Host "Submitting pipeline to KFP..." -ForegroundColor Cyan
    Push-Location python/rag-pipeline; uv run main; Pop-Location

# --- RAG Retriever ---

# Start the RAG retriever API server on http://localhost:8000
serve:
    @Write-Host "Starting RAG retriever on http://localhost:8000 ..." -ForegroundColor Cyan
    Push-Location python/rag-retriever; uv run python -m rag_retriever.main; Pop-Location

# Query the RAG retriever with a question
query question:
    Invoke-RestMethod -Method Post -Uri "http://localhost:8000/search" -ContentType "application/json" -Body (@{query="{{question}}"; top_k=5} | ConvertTo-Json)

# --- Testing ---

# Run end-to-end integration test (requires PostgreSQL via docker compose)
e2e:
    @Write-Host "Running end-to-end pipeline test..." -ForegroundColor Cyan
    Push-Location python/rag-retriever; uv run pytest ../../tests/e2e/ -v --no-cov --tb=short; Pop-Location

# --- Cross-package commands ---

# Install all packages (dev dependencies)
install-all:
    Get-ChildItem -Path python -Directory | Where-Object { Test-Path "$($_.FullName)\justfile" } | ForEach-Object { Push-Location $_.FullName; just install-dev; Pop-Location }

# Run linter + format check + typecheck across all packages
check-all:
    Get-ChildItem -Path python -Directory | Where-Object { Test-Path "$($_.FullName)\justfile" } | ForEach-Object { Push-Location $_.FullName; just check-all; Pop-Location }

# Run tests across all packages
test-all:
    Get-ChildItem -Path python -Directory | Where-Object { Test-Path "$($_.FullName)\justfile" } | ForEach-Object { Push-Location $_.FullName; just test; Pop-Location }

# Run pre-commit hooks on all files
pre-commit:
    pre-commit run --all-files
