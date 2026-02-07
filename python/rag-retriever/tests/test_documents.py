"""Tests for GET /documents/stats endpoint."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from rag_retriever.api import create_app
from rag_retriever.dependencies import get_db_session


def _make_app(session: AsyncMock) -> object:
    """
    Create a test app with overridden DB session dependency.

    Parameters
    ----------
    session : AsyncMock
        Mock database session.

    Returns
    -------
    object
        FastAPI app with dependency overrides.
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

    app.dependency_overrides[get_db_session] = _override_session  # type: ignore[union-attr]
    return app


@pytest.mark.asyncio
async def test_stats_with_data() -> None:
    """Test that GET /documents/stats returns correct counts."""
    session = AsyncMock()
    mock_result = MagicMock()
    mock_result.one.return_value = (3, 26)
    session.execute.return_value = mock_result

    app = _make_app(session)
    transport = ASGITransport(app=app)  # type: ignore[arg-type]
    async with AsyncClient(transport=transport, base_url="http://test") as http:
        resp = await http.get("/documents/stats")

    assert resp.status_code == 200
    data = resp.json()
    assert data["total_documents"] == 3
    assert data["total_chunks"] == 26
    assert data["embedding_dimension"] == 384
    assert data["model_name"] == "all-MiniLM-L6-v2"


@pytest.mark.asyncio
async def test_stats_empty_db() -> None:
    """Test that GET /documents/stats returns zeros on empty DB."""
    session = AsyncMock()
    mock_result = MagicMock()
    mock_result.one.return_value = (0, 0)
    session.execute.return_value = mock_result

    app = _make_app(session)
    transport = ASGITransport(app=app)  # type: ignore[arg-type]
    async with AsyncClient(transport=transport, base_url="http://test") as http:
        resp = await http.get("/documents/stats")

    assert resp.status_code == 200
    data = resp.json()
    assert data["total_documents"] == 0
    assert data["total_chunks"] == 0
