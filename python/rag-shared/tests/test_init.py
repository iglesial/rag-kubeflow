"""Tests for rag-shared package."""

from rag_shared import __version__


def test_version() -> None:
    """Test that package version is set."""
    assert __version__ == "0.1.0"
