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


task_inputs = TaskInputs()  # type: ignore[call-arg, unused-ignore]
