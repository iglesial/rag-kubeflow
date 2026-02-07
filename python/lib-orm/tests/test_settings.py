"""Tests for database settings."""

import pytest

from lib_orm.settings import DbSettings


def test_defaults() -> None:
    """Test that DbSettings loads correct defaults."""
    settings = DbSettings()
    assert settings.db_url == "postgresql+asyncpg://rag:rag@localhost:5432/rag"


def test_env_override(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Test that DbSettings picks up environment variables.

    Parameters
    ----------
    monkeypatch : pytest.MonkeyPatch
        Pytest monkeypatch fixture.
    """
    monkeypatch.setenv("RAG_DB_URL", "postgresql+asyncpg://test:test@db:5432/test")
    settings = DbSettings()
    assert settings.db_url == "postgresql+asyncpg://test:test@db:5432/test"
