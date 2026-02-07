"""Task inputs module for rag-retriever."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class TaskInputs(BaseSettings):
    """
    Task inputs for rag-retriever API service.

    Attributes
    ----------
    host : str
        Host address to bind the server to.
    port : int
        Port number to listen on.
    db_url : str
        Database connection URL.
    embedding_model : str
        Name of the sentence-transformers model for query embedding.
    top_k : int
        Default number of results to return from search.
    """

    model_config = SettingsConfigDict(cli_parse_args=True, cli_ignore_unknown_args=True)

    host: str = Field(
        default="0.0.0.0",
        description="Host address to bind the server to",
    )
    port: int = Field(
        default=8000,
        description="Port number to listen on",
    )
    db_url: str = Field(
        default="postgresql+asyncpg://rag:rag@localhost:5432/rag",
        description="Database connection URL",
    )
    embedding_model: str = Field(
        default="all-MiniLM-L6-v2",
        description="Name of the sentence-transformers model for query embedding",
    )
    top_k: int = Field(
        default=5,
        description="Default number of results to return from search",
    )


task_inputs = TaskInputs()  # type: ignore[call-arg, unused-ignore]
