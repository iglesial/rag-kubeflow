"""Tests for shared settings."""

import pytest

from rag_shared.settings import Settings


def test_defaults() -> None:
    """
    Test that Settings loads correct defaults.

    Verifies db_url, embedding_model, and vector_dim have expected values.
    """
    settings = Settings()
    assert settings.db_url == "postgresql+asyncpg://rag:rag@localhost:5432/rag"
    assert settings.embedding_model == "all-MiniLM-L6-v2"
    assert settings.vector_dim == 384


def test_env_override(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Test that Settings picks up environment variables.

    Parameters
    ----------
    monkeypatch : pytest.MonkeyPatch
        Pytest monkeypatch fixture.
    """
    monkeypatch.setenv("RAG_DB_URL", "postgresql+asyncpg://test:test@db:5432/test")
    monkeypatch.setenv("RAG_EMBEDDING_MODEL", "paraphrase-MiniLM-L3-v2")
    monkeypatch.setenv("RAG_VECTOR_DIM", "128")
    settings = Settings()
    assert settings.db_url == "postgresql+asyncpg://test:test@db:5432/test"
    assert settings.embedding_model == "paraphrase-MiniLM-L3-v2"
    assert settings.vector_dim == 128
