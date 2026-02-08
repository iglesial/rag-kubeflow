# Root justfile for rag-kubeflow
# Run `just --list` to see all available commands

set shell := ["powershell", "-NoProfile", "-Command"]

# Default recipe to display help
default:
    @just --list

# --- Infrastructure ---

# Start PostgreSQL via docker-compose
infra-up:
    docker compose up -d

# Stop PostgreSQL via docker-compose
infra-down:
    docker compose down

# Show infrastructure status
infra-status:
    docker compose ps

# --- Kubeflow Pipelines ---

# KFP manifest version for standalone deployment
KFP_VERSION := "2.3.0"
# Kind cluster name
KIND_CLUSTER := "rag-kubeflow"

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
