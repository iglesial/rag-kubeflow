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

# --- Docker ---

# Build all Docker images
build-images:
    docker build -t rag-loader:latest -f python/rag-loader/Dockerfile .
    docker build -t rag-embedder:latest -f python/rag-embedder/Dockerfile .
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
