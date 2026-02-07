"""Tests for dependency injection module."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from rag_retriever import dependencies


@pytest.fixture(autouse=True)
def _reset_dependencies() -> None:
    """Reset module-level state before each test."""
    dependencies._engine = None
    dependencies._embedding_client = None


def test_get_embedding_client_not_initialized() -> None:
    """Test that get_embedding_client raises when not initialized."""
    with pytest.raises(RuntimeError, match="Embedding client not initialized"):
        dependencies.get_embedding_client()


@pytest.mark.asyncio
async def test_get_db_session_not_initialized() -> None:
    """Test that get_db_session raises when engine is not initialized."""
    with pytest.raises(RuntimeError, match="Database engine not initialized"):
        async for _session in dependencies.get_db_session():
            pass  # pragma: no cover


def test_check_model_health_no_client() -> None:
    """Test model health returns False when client is None."""
    assert dependencies.check_model_health() is False


def test_check_model_health_with_client() -> None:
    """Test model health returns True when client is set."""
    dependencies._embedding_client = MagicMock()  # type: ignore[assignment]
    assert dependencies.check_model_health() is True


@pytest.mark.asyncio
async def test_check_db_health_no_engine() -> None:
    """Test DB health returns False when engine is None."""
    result = await dependencies.check_db_health()
    assert result is False


@pytest.mark.asyncio
async def test_check_db_health_connection_error() -> None:
    """Test DB health returns False on connection error."""
    mock_engine = MagicMock()
    mock_conn = AsyncMock()
    mock_conn.execute.side_effect = ConnectionRefusedError("refused")
    mock_engine.connect.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
    mock_engine.connect.return_value.__aexit__ = AsyncMock(return_value=False)

    dependencies._engine = mock_engine
    result = await dependencies.check_db_health()
    assert result is False


@pytest.mark.asyncio
async def test_init_and_shutdown() -> None:
    """Test that init and shutdown manage resources correctly."""
    mock_engine = MagicMock()
    mock_engine.dispose = AsyncMock()
    mock_client = MagicMock()

    with (
        patch("rag_retriever.dependencies.get_async_engine", return_value=mock_engine),
        patch("rag_retriever.dependencies.EmbeddingClient", return_value=mock_client),
    ):
        await dependencies.init_dependencies()

    assert dependencies._engine is mock_engine
    assert dependencies._embedding_client is mock_client

    await dependencies.shutdown_dependencies()
    mock_engine.dispose.assert_awaited_once()
    assert dependencies._engine is None
    assert dependencies._embedding_client is None
