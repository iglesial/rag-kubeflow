"""
End-to-end integration test for the full RAG pipeline.

Requires a running PostgreSQL instance (``docker compose up -d``).
Exercises the complete flow: loader -> embedder -> retriever query.
"""

import collections.abc
import json
import subprocess
from pathlib import Path

import httpx
import pytest
import pytest_asyncio
from httpx import ASGITransport

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_URL = "postgresql+asyncpg://rag:rag@localhost:5432/rag"


def _run_sql(sql: str) -> subprocess.CompletedProcess[str]:
    """
    Execute a SQL statement against the rag database via docker compose.

    Parameters
    ----------
    sql : str
        SQL statement to execute.

    Returns
    -------
    subprocess.CompletedProcess[str]
        Completed process with stdout/stderr.
    """
    return subprocess.run(
        [
            "docker",
            "compose",
            "exec",
            "-T",
            "postgres",
            "psql",
            "-U",
            "rag",
            "-d",
            "rag",
            "-c",
            sql,
        ],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        timeout=30,
    )


def _postgres_is_reachable() -> bool:
    """
    Check if PostgreSQL is reachable via docker compose.

    Returns
    -------
    bool
        True if a ``SELECT 1`` query succeeds, False otherwise.
    """
    try:
        result = _run_sql("SELECT 1")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False
    return result.returncode == 0


# Skip the entire module if PostgreSQL is not running
pytestmark = pytest.mark.skipif(
    not _postgres_is_reachable(),
    reason="PostgreSQL not reachable (run 'docker compose up -d')",
)


@pytest.fixture(scope="module")
def pipeline(tmp_path_factory: pytest.TempPathFactory) -> dict[str, object]:
    """
    Run the full ingestion pipeline: clean DB, loader, embedder.

    Parameters
    ----------
    tmp_path_factory : pytest.TempPathFactory
        Pytest factory for creating temporary directories.

    Yields
    ------
    dict[str, object]
        Pipeline metadata with keys: chunks_dir, embeddings_dir,
        num_chunks, num_embeddings.
    """
    # Clean DB before running
    result = _run_sql("DELETE FROM document_chunks")
    assert result.returncode == 0, f"DB cleanup failed:\n{result.stderr}"

    # --- Loader ---
    chunks_dir = tmp_path_factory.mktemp("chunks")
    input_dir = PROJECT_ROOT / "data" / "documents"
    result = subprocess.run(
        [
            "uv",
            "run",
            "--directory",
            str(PROJECT_ROOT / "python" / "rag-loader"),
            "python",
            "-m",
            "rag_loader.main",
            "--input_dir",
            str(input_dir),
            "--output_dir",
            str(chunks_dir),
        ],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"Loader failed:\n{result.stderr}"
    assert (chunks_dir / "chunks.json").exists(), "chunks.json not created"

    # --- Embedder ---
    embeddings_dir = tmp_path_factory.mktemp("embeddings")
    result = subprocess.run(
        [
            "uv",
            "run",
            "--directory",
            str(PROJECT_ROOT / "python" / "rag-embedder"),
            "python",
            "-m",
            "rag_embedder.main",
            "--input_dir",
            str(chunks_dir),
            "--output_dir",
            str(embeddings_dir),
            "--db_url",
            DB_URL,
        ],
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert result.returncode == 0, f"Embedder failed:\n{result.stderr}"
    assert (embeddings_dir / "embeddings.json").exists(), "embeddings.json not created"

    chunks = json.loads((chunks_dir / "chunks.json").read_text(encoding="utf-8"))
    embeddings = json.loads((embeddings_dir / "embeddings.json").read_text(encoding="utf-8"))

    yield {
        "chunks_dir": chunks_dir,
        "embeddings_dir": embeddings_dir,
        "num_chunks": len(chunks),
        "num_embeddings": len(embeddings),
    }

    # Cleanup after module
    _run_sql("DELETE FROM document_chunks")


@pytest_asyncio.fixture
async def client(
    pipeline: dict[str, object],
) -> collections.abc.AsyncGenerator[httpx.AsyncClient]:
    """
    Create an httpx client backed by the retriever app with real dependencies.

    Parameters
    ----------
    pipeline : dict[str, object]
        Pipeline fixture output (ensures ingestion ran first).

    Yields
    ------
    httpx.AsyncClient
        Async HTTP client wired to the FastAPI retriever app.
    """
    from rag_retriever.api import create_app
    from rag_retriever.dependencies import init_dependencies, shutdown_dependencies

    await init_dependencies()
    app = create_app()
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    await shutdown_dependencies()


class TestFullPipeline:
    """End-to-end tests for the loader -> embedder -> retriever flow."""

    @pytest.mark.asyncio
    async def test_search_returns_results(self, client: httpx.AsyncClient) -> None:
        """
        Search for content present in sample docs and verify results returned.

        Parameters
        ----------
        client : httpx.AsyncClient
            Test HTTP client connected to the retriever app.
        """
        resp = await client.post(
            "/search",
            json={"query": "pipeline engine kubeflow", "top_k": 5},
        )

        assert resp.status_code == 200
        data = resp.json()
        assert data["total_results"] > 0, "Expected at least one search result"

    @pytest.mark.asyncio
    async def test_top_result_similarity_above_threshold(self, client: httpx.AsyncClient) -> None:
        """
        Verify top result has similarity_score > 0.5.

        Parameters
        ----------
        client : httpx.AsyncClient
            Test HTTP client connected to the retriever app.
        """
        resp = await client.post(
            "/search",
            json={"query": "pipeline engine kubeflow", "top_k": 5},
        )

        data = resp.json()
        assert len(data["results"]) > 0, "No results to check"
        top_score = data["results"][0]["similarity_score"]
        assert top_score > 0.5, f"Top similarity {top_score} <= 0.5"

    @pytest.mark.asyncio
    async def test_top_result_matches_source_document(self, client: httpx.AsyncClient) -> None:
        """
        Verify top result for 'vector store pgvector' comes from the right doc.

        Parameters
        ----------
        client : httpx.AsyncClient
            Test HTTP client connected to the retriever app.
        """
        resp = await client.post(
            "/search",
            json={"query": "vector store pgvector cosine", "top_k": 3},
        )

        data = resp.json()
        doc_names = [r["document_name"] for r in data["results"]]
        assert any("vector" in name.lower() for name in doc_names), (
            f"Expected a vector-databases doc in results, got {doc_names}"
        )

    @pytest.mark.asyncio
    async def test_stats_after_ingestion(
        self, pipeline: dict[str, object], client: httpx.AsyncClient
    ) -> None:
        """
        Verify stats endpoint reflects ingested data.

        Parameters
        ----------
        pipeline : dict[str, object]
            Pipeline fixture output with ingestion counts.
        client : httpx.AsyncClient
            Test HTTP client connected to the retriever app.
        """
        resp = await client.get("/documents/stats")

        assert resp.status_code == 200
        data = resp.json()
        assert data["total_documents"] > 0, "Expected documents in DB"
        assert data["total_chunks"] == pipeline["num_embeddings"]
        assert data["embedding_dimension"] == 384
        assert data["model_name"] == "all-MiniLM-L6-v2"
