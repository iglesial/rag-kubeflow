"""Tests for async database utilities."""

from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker

from lib_orm.db import get_async_engine, get_async_session_factory


def test_get_async_engine() -> None:
    """Test that get_async_engine returns an AsyncEngine."""
    engine = get_async_engine("postgresql+asyncpg://rag:rag@localhost:5432/rag")
    assert isinstance(engine, AsyncEngine)


def test_get_async_session_factory() -> None:
    """
    Test that get_async_session_factory returns a sessionmaker.

    Verifies the factory is bound to the provided engine.
    """
    engine = get_async_engine("postgresql+asyncpg://rag:rag@localhost:5432/rag")
    factory = get_async_session_factory(engine)
    assert isinstance(factory, async_sessionmaker)
