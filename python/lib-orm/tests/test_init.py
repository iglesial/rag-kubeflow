"""Tests for lib-orm public API."""

from lib_orm import Base, DbSettings, DocumentChunk, get_async_engine


def test_exports() -> None:
    """Test that key classes are importable from the package root."""
    assert Base is not None
    assert DocumentChunk is not None
    assert DbSettings is not None
    assert get_async_engine is not None
