"""Async database connection utilities."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


def get_async_engine(url: str) -> AsyncEngine:
    """
    Create an async SQLAlchemy engine.

    Parameters
    ----------
    url : str
        Database connection URL (e.g. ``postgresql+asyncpg://...``).

    Returns
    -------
    AsyncEngine
        Configured async engine instance.
    """
    return create_async_engine(url, echo=False, pool_size=5, max_overflow=10)


def get_async_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """
    Create an async session factory bound to an engine.

    Parameters
    ----------
    engine : AsyncEngine
        The async engine to bind sessions to.

    Returns
    -------
    async_sessionmaker[AsyncSession]
        Factory for creating async sessions.
    """
    return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@asynccontextmanager
async def get_async_session(url: str) -> AsyncGenerator[AsyncSession]:
    """
    Yield an async database session.

    Parameters
    ----------
    url : str
        Database connection URL.

    Yields
    ------
    AsyncSession
        An active async session that is committed on success and rolled back on error.
    """
    engine = get_async_engine(url)
    session_factory = get_async_session_factory(engine)
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await engine.dispose()
