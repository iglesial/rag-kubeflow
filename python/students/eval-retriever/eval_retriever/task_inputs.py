"""Task inputs module for eval-retriever."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class TaskInputs(BaseSettings):
    """
    Task inputs for the retrieval evaluation run.

    Attributes
    ----------
    eval_csv_path : str
        Path to the ground-truth eval set CSV.
    retriever_url : str
        Base URL of the running ``rag-retriever`` service.
    top_k : int
        Number of chunks to request from the retriever for each query.
    similarity_threshold : float
        Minimum cosine similarity for retrieved chunks to be returned.
    approach_tag : str
        MLFlow tag identifying the retrieval configuration under test
        (e.g. ``baseline``, ``name-injection``, ``finetuned``).
    mlflow_tracking_uri : str
        URL of the MLFlow tracking server.
    experiment_name : str
        MLFlow experiment to log this run under.
    results_dir : str
        Directory where the per-query ``results.csv`` artifact is written
        before being uploaded to MLFlow.
    request_timeout_s : float
        Per-request HTTP timeout for calls to the retriever.
    """

    model_config = SettingsConfigDict(cli_parse_args=True, cli_ignore_unknown_args=True)

    eval_csv_path: str = Field(
        default="../../data/eval/eval_set.csv",
        description="Path to the ground-truth eval set CSV",
    )
    retriever_url: str = Field(
        default="http://localhost:8000",
        description="Base URL of the running rag-retriever service",
    )
    top_k: int = Field(
        default=5,
        ge=1,
        le=50,
        description="Number of chunks to request per query",
    )
    similarity_threshold: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Minimum cosine similarity for retrieved chunks",
    )
    approach_tag: str = Field(
        default="baseline",
        description="MLFlow tag identifying the retrieval configuration under test",
    )
    mlflow_tracking_uri: str = Field(
        default="http://localhost:5000",
        description="URL of the MLFlow tracking server",
    )
    experiment_name: str = Field(
        default="rag-retrieval-comparison",
        description="MLFlow experiment name",
    )
    results_dir: str = Field(
        default="../../data/eval-results",
        description="Directory where per-query results.csv is written",
    )
    request_timeout_s: float = Field(
        default=30.0,
        gt=0.0,
        description="HTTP timeout for each retriever request",
    )


task_inputs = TaskInputs()  # type: ignore[call-arg, unused-ignore]
