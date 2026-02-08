"""Task inputs module for rag-pipeline."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class TaskInputs(BaseSettings):
    """
    Task inputs for rag-pipeline orchestration.

    Attributes
    ----------
    pipeline_name : str
        Name of the Kubeflow pipeline.
    input_dir : str
        Directory containing input documents.
    kubeflow_host : str
        URL of the Kubeflow Pipelines API.
    compile_only : bool
        If True, compile the pipeline YAML without submitting.
    chunk_size : int
        Maximum number of characters per chunk.
    chunk_overlap : int
        Number of overlapping characters between consecutive chunks.
    db_url : str
        Database connection URL.
    embedding_model : str
        Name of the sentence-transformers model.
    batch_size : int
        Number of chunks to embed per batch.
    """

    model_config = SettingsConfigDict(cli_parse_args=True, cli_ignore_unknown_args=True)

    pipeline_name: str = Field(
        default="rag-ingestion",
        description="Name of the Kubeflow pipeline",
    )
    input_dir: str = Field(
        default="data/documents",
        description="Directory containing input documents",
    )
    kubeflow_host: str = Field(
        default="http://localhost:8080",
        description="URL of the Kubeflow Pipelines API",
    )
    compile_only: bool = Field(
        default=False,
        description="If True, compile the pipeline YAML without submitting",
    )
    chunk_size: int = Field(
        default=512,
        description="Maximum number of characters per chunk",
    )
    chunk_overlap: int = Field(
        default=64,
        description="Number of overlapping characters between consecutive chunks",
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
