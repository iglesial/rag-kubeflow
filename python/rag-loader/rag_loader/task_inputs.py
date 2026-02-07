"""Task inputs module for rag-loader."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class TaskInputs(BaseSettings):
    """
    Task inputs for rag-loader pipeline step.

    Attributes
    ----------
    input_dir : str
        Directory containing input documents to process.
    output_dir : str
        Directory to write chunked output JSON files.
    chunk_size : int
        Maximum number of characters per chunk.
    chunk_overlap : int
        Number of overlapping characters between consecutive chunks.
    """

    model_config = SettingsConfigDict(cli_parse_args=True, cli_ignore_unknown_args=True)

    input_dir: str = Field(
        default="data/documents",
        description="Directory containing input documents to process",
    )
    output_dir: str = Field(
        default="data/chunks",
        description="Directory to write chunked output JSON files",
    )
    chunk_size: int = Field(
        default=512,
        description="Maximum number of characters per chunk",
    )
    chunk_overlap: int = Field(
        default=64,
        description="Number of overlapping characters between consecutive chunks",
    )


task_inputs = TaskInputs()  # type: ignore[call-arg, unused-ignore]
