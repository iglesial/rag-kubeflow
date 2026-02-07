"""Database settings for RAG system components."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DbSettings(BaseSettings):
    """
    Database configuration for RAG system.

    Loaded from environment variables with ``RAG_`` prefix.

    Attributes
    ----------
    db_url : str
        Async database connection URL.
    """

    model_config = SettingsConfigDict(env_prefix="RAG_")

    db_url: str = Field(
        default="postgresql+asyncpg://rag:rag@localhost:5432/rag",
        description="Async database connection URL",
    )
