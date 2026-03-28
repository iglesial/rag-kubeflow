#!/usr/bin/env bash
# create-starter-repo.sh
#
# Creates the student starter repository from the reference solution.
# Copies all scaffolding as-is, copies lib-* packages as-is,
# and replaces business logic in service packages with skeleton stubs.
#
# Usage:
#   ./scripts/create-starter-repo.sh [output_dir]
#   Default output: ../rag-kubeflow-starter

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
OUT_DIR="${1:-$(cd "$SRC_DIR/.." && pwd)/rag-kubeflow-starter}"

echo "=== Creating starter repo ==="
echo "Source:  $SRC_DIR"
echo "Output:  $OUT_DIR"
echo ""

# Directories to exclude from all copies
EXCLUDES=(.venv __pycache__ .mypy_cache .pytest_cache .ruff_cache node_modules .git)

# rsync-like copy that skips EXCLUDES
# Uses tar pipe to handle excludes portably (no rsync on Git Bash by default)
copy_filtered() {
    local src="$1" dst="$2"
    mkdir -p "$dst"
    local exclude_args=()
    for ex in "${EXCLUDES[@]}"; do
        exclude_args+=(--exclude="$ex")
    done
    tar cf - -C "$(dirname "$src")" "${exclude_args[@]}" "$(basename "$src")" \
        | tar xf - -C "$(dirname "$dst")"
}

# Clean output directory (cmd fallback for Windows file locking)
rm -rf "$OUT_DIR" 2>/dev/null
if [ -d "$OUT_DIR" ] && command -v cmd &>/dev/null; then
    cmd //c "rmdir /s /q $(cygpath -w "$OUT_DIR")" 2>/dev/null
fi
mkdir -p "$OUT_DIR"

# ── 1. Copy root scaffolding as-is ──────────────────────────────────────────

echo "Copying root scaffolding..."
for f in \
    docker-compose.yml \
    pyproject.toml \
    justfile \
    .pre-commit-config.yaml \
    .gitignore \
    .python-version
do
    [ -f "$SRC_DIR/$f" ] && cp "$SRC_DIR/$f" "$OUT_DIR/$f"
done

# Copy directories
for d in infra data course specs; do
    [ -d "$SRC_DIR/$d" ] && cp -r "$SRC_DIR/$d" "$OUT_DIR/$d"
done

# Copy e2e tests
mkdir -p "$OUT_DIR/tests/e2e"
cp -r "$SRC_DIR/tests/e2e/"* "$OUT_DIR/tests/e2e/" 2>/dev/null || true
[ -f "$SRC_DIR/tests/__init__.py" ] && cp "$SRC_DIR/tests/__init__.py" "$OUT_DIR/tests/"

# ── 2. Copy lib-* packages as-is (complete implementation) ──────────────────

echo "Copying shared libraries (complete)..."
mkdir -p "$OUT_DIR/python"
for lib in lib-schemas lib-embedding lib-orm; do
    [ -d "$SRC_DIR/python/$lib" ] && copy_filtered "$SRC_DIR/python/$lib" "$OUT_DIR/python/$lib"
done

# Copy package-1 template
[ -d "$SRC_DIR/python/package-1" ] && copy_filtered "$SRC_DIR/python/package-1" "$OUT_DIR/python/package-1"

# ── 3. Copy service packages with skeleton stubs ────────────────────────────

# Helper: copy the full package, then replace specific files with stubs
copy_package_scaffold() {
    local pkg="$1"
    local pkg_dir="$SRC_DIR/python/$pkg"
    local out_pkg="$OUT_DIR/python/$pkg"

    if [ ! -d "$pkg_dir" ]; then
        echo "  SKIP $pkg (not found)"
        return
    fi

    echo "  Scaffolding $pkg..."

    # Copy everything (excluding .venv, caches, etc.)
    copy_filtered "$pkg_dir" "$out_pkg"
}

echo "Creating service package skeletons..."

# ── rag-loader ──

copy_package_scaffold "rag-loader"

cat > "$OUT_DIR/python/rag-loader/rag_loader/reader.py" << 'STUB'
"""Document reader module for rag-loader."""

from pathlib import Path

SUPPORTED_EXTENSIONS = {".txt", ".md"}


def read_documents(input_dir: str) -> list[dict[str, object]]:
    """
    Read all supported text files from a directory.

    Reads ``.txt`` and ``.md`` files (non-recursive) and returns their
    content along with metadata.

    Parameters
    ----------
    input_dir : str
        Path to the directory containing documents.

    Returns
    -------
    list[dict[str, object]]
        List of dicts with keys ``document_name``, ``content``, ``metadata``.
        Metadata contains ``file_size`` (int) and ``extension`` (str).

    Raises
    ------
    FileNotFoundError
        If ``input_dir`` does not exist.
    NotADirectoryError
        If ``input_dir`` is not a directory.
    """
    raise NotImplementedError  # TODO: implement
STUB

cat > "$OUT_DIR/python/rag-loader/rag_loader/chunker.py" << 'STUB'
"""Recursive character text splitter for rag-loader."""

SEPARATORS = ["\n\n", "\n", ". ", " ", ""]


def chunk_text(text: str, chunk_size: int = 512, chunk_overlap: int = 64) -> list[str]:
    """
    Split text into overlapping chunks using a recursive character strategy.

    Tries separators in order (paragraph, newline, sentence, word, character)
    and falls back to the next separator when a segment exceeds ``chunk_size``.

    Parameters
    ----------
    text : str
        The input text to split.
    chunk_size : int
        Maximum number of characters per chunk.
    chunk_overlap : int
        Number of overlapping characters between consecutive chunks.

    Returns
    -------
    list[str]
        List of text chunks.

    Raises
    ------
    ValueError
        If ``chunk_overlap`` is greater than or equal to ``chunk_size``.
    """
    raise NotImplementedError  # TODO: implement


def _split_recursive(text: str, chunk_size: int, sep_idx: int) -> list[str]:
    """
    Recursively split text using the separator hierarchy.

    Parameters
    ----------
    text : str
        Text to split.
    chunk_size : int
        Maximum chunk size.
    sep_idx : int
        Current index into the ``SEPARATORS`` list.

    Returns
    -------
    list[str]
        List of text segments.
    """
    raise NotImplementedError  # TODO: implement


def _merge_with_overlap(segments: list[str], chunk_size: int, chunk_overlap: int) -> list[str]:
    """
    Merge small segments into chunks and add overlap between them.

    Parameters
    ----------
    segments : list[str]
        Text segments to merge.
    chunk_size : int
        Maximum chunk size.
    chunk_overlap : int
        Target overlap between consecutive chunks.

    Returns
    -------
    list[str]
        Merged chunks with overlap.
    """
    raise NotImplementedError  # TODO: implement
STUB

cat > "$OUT_DIR/python/rag-loader/rag_loader/app.py" << 'STUB'
"""Application module for rag-loader."""


class App:
    """Document loader application for RAG system."""

    def run(self) -> None:
        """
        Run the document loader.

        Read documents from ``input_dir``, chunk them, and write JSON to ``output_dir``.
        """
        raise NotImplementedError  # TODO: implement
STUB

# ── rag-embedder ──

copy_package_scaffold "rag-embedder"

cat > "$OUT_DIR/python/rag-embedder/rag_embedder/writer.py" << 'STUB'
"""Batch writer for pgvector storage."""

from sqlalchemy.ext.asyncio import AsyncSession

from lib_schemas.schemas import ChunkWithEmbedding


async def write_chunks(session: AsyncSession, chunks: list[ChunkWithEmbedding]) -> int:
    """
    Write embedding chunks to the database with upsert logic.

    For each chunk, look up an existing ``DocumentChunk`` by
    ``(document_name, chunk_index)``. If found, update it in place.
    If not found, create a new row.

    Parameters
    ----------
    session : AsyncSession
        SQLAlchemy async session.
    chunks : list[ChunkWithEmbedding]
        Chunks with embeddings to write.

    Returns
    -------
    int
        Number of rows affected (inserted or updated).
    """
    raise NotImplementedError  # TODO: implement
STUB

cat > "$OUT_DIR/python/rag-embedder/rag_embedder/app.py" << 'STUB'
"""Application module for rag-embedder."""


class App:
    """Batch embedding and storage application for RAG system."""

    def run(self) -> None:
        """
        Run the embedder.

        Load chunks from JSON, generate embeddings, save to JSON and database.
        """
        raise NotImplementedError  # TODO: implement

    @staticmethod
    async def _write_to_db(results: list) -> None:
        """
        Write embedding results to the database.

        Parameters
        ----------
        results : list
            List of ``ChunkWithEmbedding`` objects.
        """
        raise NotImplementedError  # TODO: implement
STUB

# ── rag-retriever ──

copy_package_scaffold "rag-retriever"

cat > "$OUT_DIR/python/rag-retriever/rag_retriever/dependencies.py" << 'STUB'
"""FastAPI dependency injection and shared resource management."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from lib_embedding.embedding import EmbeddingClient

_engine: AsyncEngine | None = None
_embedding_client: EmbeddingClient | None = None


async def init_dependencies() -> None:
    """Initialize the database engine and embedding client."""
    raise NotImplementedError  # TODO: implement


async def shutdown_dependencies() -> None:
    """Dispose the database engine and release resources."""
    raise NotImplementedError  # TODO: implement


async def get_db_session() -> AsyncGenerator[AsyncSession]:
    """
    Yield an async database session.

    Commits on success, rolls back on error.

    Yields
    ------
    AsyncSession
        An active database session.

    Raises
    ------
    RuntimeError
        If the database engine has not been initialized.
    """
    raise NotImplementedError  # TODO: implement
    yield  # type: ignore[misc]  # make it a generator


def get_embedding_client() -> EmbeddingClient:
    """
    Return the pre-loaded embedding client.

    Returns
    -------
    EmbeddingClient
        The embedding client singleton.

    Raises
    ------
    RuntimeError
        If the embedding client has not been initialized.
    """
    raise NotImplementedError  # TODO: implement


async def check_db_health() -> bool:
    """
    Check database connectivity by executing ``SELECT 1``.

    Returns
    -------
    bool
        True if the database is reachable.
    """
    raise NotImplementedError  # TODO: implement


def check_model_health() -> bool:
    """
    Check whether the embedding model is loaded.

    Returns
    -------
    bool
        True if ``_embedding_client`` is not None.
    """
    raise NotImplementedError  # TODO: implement
STUB

cat > "$OUT_DIR/python/rag-retriever/rag_retriever/api.py" << 'STUB'
"""FastAPI application factory."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """
    Manage application lifespan: init and shutdown dependencies.

    Parameters
    ----------
    app : FastAPI
        The FastAPI application instance.

    Yields
    ------
    None
    """
    raise NotImplementedError  # TODO: implement
    yield  # type: ignore[misc]


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns
    -------
    FastAPI
        Configured application with routers and lifespan.
    """
    raise NotImplementedError  # TODO: implement
STUB

mkdir -p "$OUT_DIR/python/rag-retriever/rag_retriever/routes"
[ -f "$SRC_DIR/python/rag-retriever/rag_retriever/routes/__init__.py" ] && \
    cp "$SRC_DIR/python/rag-retriever/rag_retriever/routes/__init__.py" \
       "$OUT_DIR/python/rag-retriever/rag_retriever/routes/__init__.py"

cat > "$OUT_DIR/python/rag-retriever/rag_retriever/routes/health.py" << 'STUB'
"""Health and readiness probe endpoints."""

from typing import Any

from fastapi import APIRouter, Response

router = APIRouter()


@router.get("/health")
async def health() -> dict[str, str]:
    """
    Return a simple health check.

    Returns
    -------
    dict[str, str]
        Always ``{"status": "ok"}``.
    """
    raise NotImplementedError  # TODO: implement


@router.get("/ready")
async def ready(response: Response) -> dict[str, Any]:
    """
    Check readiness of database and embedding model.

    Returns 200 if all healthy, 503 otherwise.

    Parameters
    ----------
    response : Response
        FastAPI response object (to set status code).

    Returns
    -------
    dict[str, Any]
        Dict with keys ``status``, ``db``, ``model``.
    """
    raise NotImplementedError  # TODO: implement
STUB

cat > "$OUT_DIR/python/rag-retriever/rag_retriever/routes/search.py" << 'STUB'
"""Semantic search endpoint."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from lib_embedding.embedding import EmbeddingClient
from lib_schemas.schemas import SearchRequest, SearchResponse

from rag_retriever.dependencies import get_db_session, get_embedding_client

router = APIRouter()


@router.post("/search", response_model=SearchResponse)
async def search(
    body: SearchRequest,
    session: AsyncSession = Depends(get_db_session),
    client: EmbeddingClient = Depends(get_embedding_client),
) -> SearchResponse:
    """
    Perform semantic search against pgvector.

    Encode the query, search by cosine similarity, return ranked results.

    Parameters
    ----------
    body : SearchRequest
        Search parameters (query, top_k, similarity_threshold).
    session : AsyncSession
        Database session (injected).
    client : EmbeddingClient
        Embedding client (injected).

    Returns
    -------
    SearchResponse
        Ranked search results with timing information.
    """
    raise NotImplementedError  # TODO: implement
STUB

cat > "$OUT_DIR/python/rag-retriever/rag_retriever/routes/documents.py" << 'STUB'
"""Document statistics endpoint."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from lib_schemas.schemas import StatsResponse

from rag_retriever.dependencies import get_db_session

router = APIRouter(prefix="/documents")


@router.get("/stats", response_model=StatsResponse)
async def stats(
    session: AsyncSession = Depends(get_db_session),
) -> StatsResponse:
    """
    Return document and chunk statistics.

    Parameters
    ----------
    session : AsyncSession
        Database session (injected).

    Returns
    -------
    StatsResponse
        Total documents, chunks, embedding dimension, and model name.
    """
    raise NotImplementedError  # TODO: implement
STUB

cat > "$OUT_DIR/python/rag-retriever/rag_retriever/app.py" << 'STUB'
"""Application module for rag-retriever."""


class App:
    """RAG retriever API application."""

    def run(self) -> None:
        """
        Run the retriever API server.

        Start uvicorn with the FastAPI app factory.
        """
        raise NotImplementedError  # TODO: implement
STUB

# ── rag-pipeline ──

copy_package_scaffold "rag-pipeline"

mkdir -p "$OUT_DIR/python/rag-pipeline/rag_pipeline/components"
[ -f "$SRC_DIR/python/rag-pipeline/rag_pipeline/components/__init__.py" ] && \
    cp "$SRC_DIR/python/rag-pipeline/rag_pipeline/components/__init__.py" \
       "$OUT_DIR/python/rag-pipeline/rag_pipeline/components/__init__.py"

cat > "$OUT_DIR/python/rag-pipeline/rag_pipeline/components/loader.py" << 'STUB'
"""KFP container component for the document loader."""

from kfp import dsl

LOADER_IMAGE = "rag-loader:local"


@dsl.container_component
def loader_component(
    input_dir: str,
    chunk_size: int,
    chunk_overlap: int,
    chunks_artifact: dsl.Output[dsl.Artifact],
) -> dsl.ContainerSpec:
    """
    KFP component that runs rag-loader in a container.

    Parameters
    ----------
    input_dir : str
        Path to documents inside the container.
    chunk_size : int
        Maximum characters per chunk.
    chunk_overlap : int
        Overlap between consecutive chunks.
    chunks_artifact : dsl.Output[dsl.Artifact]
        Output artifact for chunked JSON.

    Returns
    -------
    dsl.ContainerSpec
        Container specification for the loader.
    """
    raise NotImplementedError  # TODO: implement
STUB

cat > "$OUT_DIR/python/rag-pipeline/rag_pipeline/components/embedder.py" << 'STUB'
"""KFP container component for the embedder."""

from kfp import dsl

EMBEDDER_IMAGE = "rag-embedder:local"


@dsl.container_component
def embedder_component(
    chunks_artifact: dsl.Input[dsl.Artifact],
    db_url: str,
    embedding_model: str,
    batch_size: int,
    embeddings_artifact: dsl.Output[dsl.Artifact],
) -> dsl.ContainerSpec:
    """
    KFP component that runs rag-embedder in a container.

    Parameters
    ----------
    chunks_artifact : dsl.Input[dsl.Artifact]
        Input artifact from the loader (chunked JSON).
    db_url : str
        PostgreSQL connection string.
    embedding_model : str
        Sentence-transformers model name.
    batch_size : int
        Batch size for embedding.
    embeddings_artifact : dsl.Output[dsl.Artifact]
        Output artifact for embeddings JSON.

    Returns
    -------
    dsl.ContainerSpec
        Container specification for the embedder.
    """
    raise NotImplementedError  # TODO: implement
STUB

cat > "$OUT_DIR/python/rag-pipeline/rag_pipeline/pipeline.py" << 'STUB'
"""KFP pipeline definition for RAG ingestion."""

from kfp import dsl

from rag_pipeline.components.embedder import embedder_component
from rag_pipeline.components.loader import loader_component


@dsl.pipeline(
    name="RAG Ingestion Pipeline",
    description="Load documents, chunk, embed, and store in pgvector.",
)
def rag_ingestion_pipeline(
    input_dir: str = "/data/documents",
    chunk_size: int = 512,
    chunk_overlap: int = 64,
    db_url: str = "postgresql+asyncpg://rag:rag@host.docker.internal:5432/rag",
    embedding_model: str = "all-MiniLM-L6-v2",
    batch_size: int = 32,
) -> None:
    """
    RAG ingestion pipeline: loader -> embedder.

    Parameters
    ----------
    input_dir : str
        Path to documents inside the loader container.
    chunk_size : int
        Maximum characters per chunk.
    chunk_overlap : int
        Overlap between consecutive chunks.
    db_url : str
        PostgreSQL connection string (use host.docker.internal for Kind).
    embedding_model : str
        Sentence-transformers model name.
    batch_size : int
        Batch size for embedding.
    """
    raise NotImplementedError  # TODO: implement
STUB

cat > "$OUT_DIR/python/rag-pipeline/rag_pipeline/app.py" << 'STUB'
"""Application module for rag-pipeline."""

PIPELINE_YAML = "rag-ingestion-pipeline.yaml"


class App:
    """Pipeline compiler and submitter application."""

    def run(self) -> None:
        """
        Compile and optionally submit the KFP pipeline.

        If ``compile_only`` is True, writes YAML and exits.
        Otherwise, submits the pipeline to the KFP cluster.
        """
        raise NotImplementedError  # TODO: implement
STUB

# ── 4. Remove solution-specific files ───────────────────────────────────────

echo "Cleaning up..."

# Remove CLAUDE.md (reference-repo specific)
rm -f "$OUT_DIR/CLAUDE.md"

# Remove .claude directory (reference-repo specific)
rm -rf "$OUT_DIR/.claude"

# Remove specs/decisions.md and specs/epics.md (reference-only)
# Keep other specs as student reference material

# Remove data/chunks and data/embeddings (generated output)
rm -rf "$OUT_DIR/data/chunks" "$OUT_DIR/data/embeddings"

# ── 5. Create starter README ───────────────────────────────────────────────

cat > "$OUT_DIR/README.md" << 'README'
# RAG Kubeflow — Starter Template

Système RAG (Retrieval-Augmented Generation) avec FastAPI, PostgreSQL+pgvector et Kubeflow Pipelines.

## Démarrage rapide

```bash
# 1. Installer les outils (voir course/setup-guide.md)
# 2. Démarrer PostgreSQL
docker compose up -d

# 3. Installer les dépendances du premier package
cd python/rag-loader && just install-dev

# 4. Lancer les tests (ils échoueront — c'est normal !)
just test
```

## Structure

```
python/
├── lib-schemas/       # Schémas Pydantic partagés (fourni)
├── lib-embedding/     # Client d'embedding (fourni)
├── lib-orm/           # ORM asynchrone (fourni)
├── rag-loader/        # À implémenter (Session 1)
├── rag-embedder/      # À implémenter (Session 2)
├── rag-retriever/     # À implémenter (Session 2)
└── rag-pipeline/      # À implémenter (Session 3)
```

## Guides de session

- [Guide d'installation](course/setup-guide.md)
- [Session 1 — Fondations](course/session-1.md)
- [Session 2 — Embedding et API](course/session-2.md)
- [Session 3 — Orchestration Kubernetes](course/session-3.md)

## Commandes utiles

```bash
just --list            # voir toutes les recettes
just load              # exécuter le loader
just embed             # exécuter l'embedder
just pipeline          # load + embed
just serve             # démarrer l'API (http://localhost:8000)
just query "question"  # interroger l'API
just test-all          # tests de tous les packages
just check-all         # lint + typecheck
just e2e               # test d'intégration
```
README

# ── 6. Summary ──────────────────────────────────────────────────────────────

# ── 6. Git init + GitHub push ───────────────────────────────────────────────

REPO_NAME="${GITHUB_REPO_NAME:-rag-kubeflow-starter}"
GITHUB_ORG="${GITHUB_ORG:-iglesial}"

echo "Initializing git repo..."
cd "$OUT_DIR"
git init -b main
git add -A
git commit -m "Initial starter template"

if command -v gh &>/dev/null; then
    echo ""
    echo "Creating GitHub repo '$REPO_NAME' (public, template)..."
    if [ -n "$GITHUB_ORG" ]; then
        gh repo create "$GITHUB_ORG/$REPO_NAME" --public --source=. --push
    else
        gh repo create "$REPO_NAME" --public --source=. --push
    fi
    # Mark as template repo
    OWNER=$(gh repo view --json owner -q '.owner.login')
    gh api -X PATCH "repos/$OWNER/$REPO_NAME" -f is_template=true
    echo ""
    echo "=== Done! ==="
    gh repo view --web 2>/dev/null || echo "Repo: https://github.com/$OWNER/$REPO_NAME"
else
    echo ""
    echo "=== Starter repo created (local only — gh CLI not found) ==="
    echo "Location: $OUT_DIR"
    echo "To push manually:"
    echo "  cd $OUT_DIR"
    echo "  gh repo create $REPO_NAME --public --source=. --push"
fi

echo ""
echo "Given complete:"
echo "  - docker-compose.yml, infra/, .pre-commit-config.yaml"
echo "  - python/lib-schemas/, python/lib-embedding/, python/lib-orm/"
echo "  - tests/ (all test suites)"
echo "  - course/ (session guides + fiche de cours)"
echo ""
echo "Skeleton stubs (students implement):"
echo "  - python/rag-loader/rag_loader/{reader,chunker,app}.py"
echo "  - python/rag-embedder/rag_embedder/{writer,app}.py"
echo "  - python/rag-retriever/rag_retriever/{api,dependencies,app,routes/*}.py"
echo "  - python/rag-pipeline/rag_pipeline/{pipeline,app,components/*}.py"
