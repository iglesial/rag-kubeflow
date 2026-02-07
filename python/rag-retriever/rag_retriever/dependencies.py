"""FastAPI dependency injection for database sessions and embedding client."""

from collections.abc import AsyncGenerator

from lib_embedding.embedding import EmbeddingClient
from lib_orm.db import get_async_engine, get_async_session_factory
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from rag_retriever.task_inputs import task_inputs

_engine: AsyncEngine | None = None
_embedding_client: EmbeddingClient | None = None


async def init_dependencies() -> None:
    """
    Initialize shared resources at application startup.

    Creates the async database engine and loads the embedding model.
    """
    global _engine, _embedding_client  # noqa: PLW0603
    _engine = get_async_engine(task_inputs.db_url)
    _embedding_client = EmbeddingClient(task_inputs.embedding_model)


async def shutdown_dependencies() -> None:
    """Dispose of shared resources at application shutdown."""
    global _engine, _embedding_client  # noqa: PLW0603
    if _engine is not None:
        await _engine.dispose()
        _engine = None
    _embedding_client = None


async def get_db_session() -> AsyncGenerator[AsyncSession]:
    """
    Yield an async database session for a single request.

    Yields
    ------
    AsyncSession
        An active async session that is committed on success and rolled back
        on error.

    Raises
    ------
    RuntimeError
        If called before ``init_dependencies``.
    """
    if _engine is None:
        msg = "Database engine not initialized"
        raise RuntimeError(msg)
    factory = get_async_session_factory(_engine)
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


def get_embedding_client() -> EmbeddingClient:
    """
    Return the shared embedding client.

    Returns
    -------
    EmbeddingClient
        The pre-loaded embedding client.

    Raises
    ------
    RuntimeError
        If called before ``init_dependencies``.
    """
    if _embedding_client is None:
        msg = "Embedding client not initialized"
        raise RuntimeError(msg)
    return _embedding_client


async def check_db_health() -> bool:
    """
    Check whether the database is reachable.

    Returns
    -------
    bool
        True if ``SELECT 1`` succeeds, False otherwise.
    """
    if _engine is None:
        return False
    try:
        async with _engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception:  # noqa: BLE001
        return False


def check_model_health() -> bool:
    """
    Check whether the embedding model is loaded.

    Returns
    -------
    bool
        True if the embedding client is available.
    """
    return _embedding_client is not None
