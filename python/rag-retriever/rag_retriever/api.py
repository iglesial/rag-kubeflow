"""FastAPI application factory."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from rag_retriever.dependencies import init_dependencies, shutdown_dependencies
from rag_retriever.routes.documents import router as documents_router
from rag_retriever.routes.health import router as health_router
from rag_retriever.routes.search import router as search_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """
    Manage application startup and shutdown.

    Parameters
    ----------
    app : FastAPI
        The FastAPI application instance.

    Yields
    ------
    None
        Yields control to the application during its lifetime.
    """
    print("Starting up: initializing DB engine and embedding model...")
    await init_dependencies()
    print("Startup complete: all dependencies ready")
    yield
    print("Shutting down: releasing resources...")
    await shutdown_dependencies()
    print("Shutdown complete")


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns
    -------
    FastAPI
        Configured FastAPI application with all routes registered.
    """
    app = FastAPI(
        title="RAG Retriever",
        description="Semantic search API for RAG system with pgvector",
        version="0.1.0",
        lifespan=lifespan,
    )
    app.include_router(health_router)
    app.include_router(search_router)
    app.include_router(documents_router)
    return app
