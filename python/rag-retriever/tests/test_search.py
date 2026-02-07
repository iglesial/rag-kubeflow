"""Tests for POST /search endpoint."""

import uuid
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from rag_retriever.api import create_app
from rag_retriever.dependencies import get_db_session, get_embedding_client


def _make_app(session: AsyncMock, client: MagicMock) -> FastAPI:
    """
    Create a test app with overridden dependencies.

    Parameters
    ----------
    session : AsyncMock
        Mock database session.
    client : MagicMock
        Mock embedding client.

    Returns
    -------
    FastAPI
        App with dependency overrides.
    """
    with patch("rag_retriever.api.lifespan") as mock_lifespan:

        @asynccontextmanager
        async def _noop(app):  # type: ignore[no-untyped-def]  # noqa: ANN001
            yield

        mock_lifespan.side_effect = _noop
        app = create_app()

    async def _override_session() -> AsyncGenerator[AsyncMock]:
        """
        Yield the mock session.

        Yields
        ------
        AsyncMock
            The mock database session.
        """
        yield session

    app.dependency_overrides[get_db_session] = _override_session
    app.dependency_overrides[get_embedding_client] = lambda: client
    return app


def _mock_row(
    doc_name: str, content: str, similarity: float, chunk_id: uuid.UUID | None = None
) -> MagicMock:
    """
    Create a mock DB result row.

    Parameters
    ----------
    doc_name : str
        Document name.
    content : str
        Chunk content.
    similarity : float
        Cosine similarity score.
    chunk_id : uuid.UUID | None
        Optional chunk ID. Generated if None.

    Returns
    -------
    MagicMock
        Mock row with DocumentChunk and similarity attributes.
    """
    row = MagicMock()
    row.DocumentChunk.id = chunk_id or uuid.uuid4()
    row.DocumentChunk.document_name = doc_name
    row.DocumentChunk.content = content
    row.DocumentChunk.metadata_ = {}
    row.similarity = similarity
    return row


@pytest.mark.asyncio
async def test_search_returns_results() -> None:
    """Test that POST /search returns ranked results."""
    session = AsyncMock()
    mock_result = MagicMock()
    mock_result.all.return_value = [
        _mock_row("doc1.md", "hello world", 0.95),
        _mock_row("doc2.md", "foo bar", 0.80),
    ]
    session.execute.return_value = mock_result

    client = MagicMock()
    client.encode.return_value = [[0.1] * 384]

    app = _make_app(session, client)
    transport = ASGITransport(app=app)  # type: ignore[arg-type]
    async with AsyncClient(transport=transport, base_url="http://test") as http:
        resp = await http.post("/search", json={"query": "hello", "top_k": 3})

    assert resp.status_code == 200
    data = resp.json()
    assert data["query"] == "hello"
    assert data["total_results"] == 2
    assert len(data["results"]) == 2
    assert data["results"][0]["similarity_score"] == 0.95
    assert data["results"][1]["similarity_score"] == 0.80
    assert "embedding_time_ms" in data
    assert "search_time_ms" in data
    client.encode.assert_called_once_with(["hello"])


@pytest.mark.asyncio
async def test_search_empty_db() -> None:
    """Test that POST /search on empty DB returns empty results."""
    session = AsyncMock()
    mock_result = MagicMock()
    mock_result.all.return_value = []
    session.execute.return_value = mock_result

    client = MagicMock()
    client.encode.return_value = [[0.1] * 384]

    app = _make_app(session, client)
    transport = ASGITransport(app=app)  # type: ignore[arg-type]
    async with AsyncClient(transport=transport, base_url="http://test") as http:
        resp = await http.post("/search", json={"query": "something"})

    assert resp.status_code == 200
    data = resp.json()
    assert data["total_results"] == 0
    assert data["results"] == []


@pytest.mark.asyncio
async def test_search_empty_query_rejected() -> None:
    """Test that POST /search with empty query returns 422."""
    session = AsyncMock()
    client = MagicMock()

    app = _make_app(session, client)
    transport = ASGITransport(app=app)  # type: ignore[arg-type]
    async with AsyncClient(transport=transport, base_url="http://test") as http:
        resp = await http.post("/search", json={"query": "", "top_k": 5})

    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_search_top_k_one() -> None:
    """Test that POST /search with top_k=1 returns at most 1 result."""
    chunk_id = uuid.uuid4()
    session = AsyncMock()
    mock_result = MagicMock()
    mock_result.all.return_value = [
        _mock_row("doc1.md", "best match", 0.99, chunk_id),
    ]
    session.execute.return_value = mock_result

    client = MagicMock()
    client.encode.return_value = [[0.1] * 384]

    app = _make_app(session, client)
    transport = ASGITransport(app=app)  # type: ignore[arg-type]
    async with AsyncClient(transport=transport, base_url="http://test") as http:
        resp = await http.post("/search", json={"query": "test", "top_k": 1})

    assert resp.status_code == 200
    data = resp.json()
    assert data["total_results"] == 1
    assert data["results"][0]["chunk_id"] == str(chunk_id)
    assert data["results"][0]["content"] == "best match"


@pytest.mark.asyncio
async def test_search_invalid_top_k() -> None:
    """Test that POST /search with top_k=0 returns 422."""
    session = AsyncMock()
    client = MagicMock()

    app = _make_app(session, client)
    transport = ASGITransport(app=app)  # type: ignore[arg-type]
    async with AsyncClient(transport=transport, base_url="http://test") as http:
        resp = await http.post("/search", json={"query": "test", "top_k": 0})

    assert resp.status_code == 422
