"""Task inputs module for rag-viz."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class TaskInputs(BaseSettings):
    """
    Task inputs for UMAP embedding visualization.

    Attributes
    ----------
    input_file : str
        Path to the embeddings JSON file.
    output_file : str
        Path for the output HTML visualization.
    n_neighbors : int
        UMAP n_neighbors parameter (local neighborhood size).
    min_dist : float
        UMAP min_dist parameter (minimum distance between points).
    metric : str
        UMAP distance metric.
    random_state : int
        Random seed for reproducibility.
    content_truncate_length : int
        Maximum characters of chunk content shown in hover tooltip.
    query_file : str
        Path to a SearchResponse JSON file (optional, for query overlay).
    plot_title : str
        Title for the scatter plot.
    point_size : int
        Scatter plot marker size.
    """

    model_config = SettingsConfigDict(cli_parse_args=True, cli_ignore_unknown_args=True)

    input_file: str = Field(
        default="../../data/embeddings/embeddings.json",
        description="Path to the embeddings JSON file",
    )
    output_file: str = Field(
        default="data/viz/embeddings_viz.html",
        description="Path for the output HTML visualization",
    )
    n_neighbors: int = Field(
        default=15,
        description="UMAP n_neighbors parameter (local neighborhood size)",
    )
    min_dist: float = Field(
        default=0.1,
        description="UMAP min_dist parameter (minimum distance between points)",
    )
    metric: str = Field(
        default="cosine",
        description="UMAP distance metric",
    )
    random_state: int = Field(
        default=42,
        description="Random seed for reproducibility",
    )
    content_truncate_length: int = Field(
        default=200,
        description="Maximum characters of chunk content shown in hover tooltip",
    )
    query_file: str = Field(
        default="",
        description="Path to a SearchResponse JSON file (optional, for query overlay)",
    )
    plot_title: str = Field(
        default="RAG Embeddings UMAP Projection",
        description="Title for the scatter plot",
    )
    point_size: int = Field(
        default=6,
        description="Scatter plot marker size",
    )


task_inputs = TaskInputs()  # type: ignore[call-arg, unused-ignore]
