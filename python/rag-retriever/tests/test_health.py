"""Tests for health and readiness endpoints."""

from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from rag_retriever.api import create_app


@pytest.fixture
def app_no_lifespan() -> object:
    """
    Create a FastAPI app without running the lifespan.

    Returns
    -------
    FastAPI
        A FastAPI app instance for testing.
    """
    with patch("rag_retriever.api.lifespan") as mock_lifespan:
        from contextlib import asynccontextmanager

        @asynccontextmanager
        async def _noop_lifespan(app):  # type: ignore[no-untyped-def]  # noqa: ANN001
            yield

        mock_lifespan.side_effect = _noop_lifespan
        yield create_app()


@pytest.mark.asyncio
async def test_health_returns_ok(app_no_lifespan: object) -> None:
    """
    Test that GET /health returns status ok.

    Parameters
    ----------
    app_no_lifespan : object
        FastAPI app fixture without lifespan.
    """
    transport = ASGITransport(app=app_no_lifespan)  # type: ignore[arg-type]
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/health")

    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_ready_all_healthy(app_no_lifespan: object) -> None:
    """
    Test that GET /ready returns 200 when DB and model are healthy.

    Parameters
    ----------
    app_no_lifespan : object
        FastAPI app fixture without lifespan.
    """
    with (
        patch(
            "rag_retriever.routes.health.check_db_health",
            new_callable=AsyncMock,
            return_value=True,
        ),
        patch("rag_retriever.routes.health.check_model_health", return_value=True),
    ):
        transport = ASGITransport(app=app_no_lifespan)  # type: ignore[arg-type]
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/ready")

    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ready"
    assert data["db"] is True
    assert data["model"] is True


@pytest.mark.asyncio
async def test_ready_db_down(app_no_lifespan: object) -> None:
    """
    Test that GET /ready returns 503 when DB is unreachable.

    Parameters
    ----------
    app_no_lifespan : object
        FastAPI app fixture without lifespan.
    """
    with (
        patch(
            "rag_retriever.routes.health.check_db_health",
            new_callable=AsyncMock,
            return_value=False,
        ),
        patch("rag_retriever.routes.health.check_model_health", return_value=True),
    ):
        transport = ASGITransport(app=app_no_lifespan)  # type: ignore[arg-type]
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/ready")

    assert resp.status_code == 503
    data = resp.json()
    assert data["status"] == "not_ready"
    assert data["db"] is False
    assert data["model"] is True


@pytest.mark.asyncio
async def test_ready_model_not_loaded(app_no_lifespan: object) -> None:
    """
    Test that GET /ready returns 503 when model is not loaded.

    Parameters
    ----------
    app_no_lifespan : object
        FastAPI app fixture without lifespan.
    """
    with (
        patch(
            "rag_retriever.routes.health.check_db_health",
            new_callable=AsyncMock,
            return_value=True,
        ),
        patch("rag_retriever.routes.health.check_model_health", return_value=False),
    ):
        transport = ASGITransport(app=app_no_lifespan)  # type: ignore[arg-type]
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/ready")

    assert resp.status_code == 503
    data = resp.json()
    assert data["status"] == "not_ready"
    assert data["db"] is True
    assert data["model"] is False
