"""Tests for lib-embedding public API."""

from lib_embedding import EmbeddingClient, EmbeddingSettings


def test_exports() -> None:
    """Test that key classes are importable from the package root."""
    assert EmbeddingClient is not None
    assert EmbeddingSettings is not None
