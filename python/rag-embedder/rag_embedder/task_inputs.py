"""Task inputs module for rag-embedder."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class TaskInputs(BaseSettings):
    """
    Task inputs for rag-embedder pipeline step.

    Attributes
    ----------
    input_dir : str
        Directory containing chunk JSON files to embed.
    output_dir : str
        Directory to save embeddings as JSON.
    db_url : str
        Database connection URL.
    embedding_model : str
        Name of the sentence-transformers model.
    batch_size : int
        Number of chunks to embed per batch.
    """

    model_config = SettingsConfigDict(cli_parse_args=True, cli_ignore_unknown_args=True)

    input_dir: str = Field(
        default="data/chunks",
        description="Directory containing chunk JSON files to embed",
    )
    output_dir: str = Field(
        default="data/embeddings",
        description="Directory to save embeddings as JSON",
    )
    db_url: str = Field(
        default="postgresql+asyncpg://rag:rag@localhost:5432/rag",
        description="Database connection URL",
    )
    embedding_model: str = Field(
        default="all-MiniLM-L6-v2",
        description="Name of the sentence-transformers model",
    )
    batch_size: int = Field(
        default=32,
        description="Number of chunks to embed per batch",
    )


task_inputs = TaskInputs()  # type: ignore[call-arg, unused-ignore]
