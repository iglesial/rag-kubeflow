"""Tests for embedding settings."""

import pytest

from lib_embedding.settings import EmbeddingSettings


def test_defaults() -> None:
    """Test that EmbeddingSettings loads correct defaults."""
    settings = EmbeddingSettings()
    assert settings.embedding_model == "all-MiniLM-L6-v2"
    assert settings.vector_dim == 384


def test_env_override(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Test that EmbeddingSettings picks up environment variables.

    Parameters
    ----------
    monkeypatch : pytest.MonkeyPatch
        Pytest monkeypatch fixture.
    """
    monkeypatch.setenv("RAG_EMBEDDING_MODEL", "paraphrase-MiniLM-L3-v2")
    monkeypatch.setenv("RAG_VECTOR_DIM", "128")
    settings = EmbeddingSettings()
    assert settings.embedding_model == "paraphrase-MiniLM-L3-v2"
    assert settings.vector_dim == 128
