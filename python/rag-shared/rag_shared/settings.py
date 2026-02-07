"""Shared settings for RAG system components."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Shared configuration for RAG system.

    Loaded from environment variables with ``RAG_`` prefix.

    Attributes
    ----------
    db_url : str
        Async database connection URL.
    embedding_model : str
        Name of the sentence-transformers model.
    vector_dim : int
        Dimension of embedding vectors.
    """

    model_config = SettingsConfigDict(env_prefix="RAG_")

    db_url: str = Field(
        default="postgresql+asyncpg://rag:rag@localhost:5432/rag",
        description="Async database connection URL",
    )
    embedding_model: str = Field(
        default="all-MiniLM-L6-v2",
        description="Name of the sentence-transformers model",
    )
    vector_dim: int = Field(
        default=384,
        description="Dimension of embedding vectors",
    )
