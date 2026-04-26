"""Tests for rag-loader public API."""

from rag_loader import __version__


def test_version() -> None:
    """Test that the package version is set."""
    assert __version__ == "0.1.0"
