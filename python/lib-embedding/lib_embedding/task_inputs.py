"""Task inputs module for lib-embedding."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class TaskInputs(BaseSettings):
    """Task inputs for lib-embedding diagnostics."""

    model_config = SettingsConfigDict(cli_parse_args=True, cli_ignore_unknown_args=True)

    embedding_model: str = Field(
        default="all-MiniLM-L6-v2",
        description="Name of the sentence-transformers model",
    )
    vector_dim: int = Field(
        default=384,
        description="Dimension of embedding vectors",
    )


task_inputs = TaskInputs()  # type: ignore[call-arg, unused-ignore]
