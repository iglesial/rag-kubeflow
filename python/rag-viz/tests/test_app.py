"""Tests for rag-viz application."""

import json
import random
from pathlib import Path
from unittest.mock import patch

from rag_viz.app import App
from rag_viz.task_inputs import TaskInputs


def _make_chunks(n: int = 10, dim: int = 384) -> list[dict[str, object]]:
    """
    Generate synthetic embedding chunks.

    Parameters
    ----------
    n : int
        Number of chunks to generate.
    dim : int
        Embedding vector dimension.

    Returns
    -------
    list[dict[str, object]]
        List of chunk dictionaries with embeddings.
    """
    random.seed(42)
    return [
        {
            "document_name": f"doc-{i % 3}.md",
            "chunk_index": i,
            "content": f"This is chunk number {i} with some content for testing.",
            "metadata": {"extension": ".md"},
            "embedding": [random.gauss(0, 1) for _ in range(dim)],
        }
        for i in range(n)
    ]


def _mock_inputs(mock: object, input_file: str, output_file: str, query_file: str = "") -> None:
    """
    Configure mock task_inputs with common defaults.

    Parameters
    ----------
    mock : object
        The mock object to configure.
    input_file : str
        Path to the embeddings JSON file.
    output_file : str
        Path for the output HTML file.
    query_file : str
        Path to a SearchResponse JSON file.
    """
    mock.input_file = input_file  # type: ignore[attr-defined]
    mock.output_file = output_file  # type: ignore[attr-defined]
    mock.n_neighbors = 3  # type: ignore[attr-defined]
    mock.min_dist = 0.1  # type: ignore[attr-defined]
    mock.metric = "cosine"  # type: ignore[attr-defined]
    mock.random_state = 42  # type: ignore[attr-defined]
    mock.content_truncate_length = 50  # type: ignore[attr-defined]
    mock.plot_title = "Test Plot"  # type: ignore[attr-defined]
    mock.point_size = 6  # type: ignore[attr-defined]
    mock.query_file = query_file  # type: ignore[attr-defined]


class TestTaskInputs:
    """Tests for TaskInputs defaults."""

    def test_defaults(self) -> None:
        """Verify all TaskInputs fields have expected defaults."""
        with patch("sys.argv", ["test"]):
            inputs = TaskInputs()
        assert inputs.input_file == "../../data/embeddings/embeddings.json"
        assert inputs.output_file == "data/viz/embeddings_viz.html"
        assert inputs.n_neighbors == 15
        assert inputs.min_dist == 0.1
        assert inputs.metric == "cosine"
        assert inputs.random_state == 42
        assert inputs.content_truncate_length == 200
        assert inputs.query_file == ""
        assert inputs.plot_title == "RAG Embeddings UMAP Projection"
        assert inputs.point_size == 6


class TestApp:
    """Tests for the App visualization pipeline."""

    def test_run_generates_html(self, tmp_path: Path) -> None:
        """
        Run the full pipeline on synthetic data and verify HTML output.

        Parameters
        ----------
        tmp_path : Path
            Pytest temporary directory fixture.
        """
        chunks = _make_chunks()
        input_file = tmp_path / "embeddings.json"
        input_file.write_text(json.dumps(chunks), encoding="utf-8")
        output_file = tmp_path / "viz.html"

        with patch("rag_viz.app.task_inputs") as mock_inputs:
            _mock_inputs(mock_inputs, str(input_file), str(output_file))
            App().run()

        assert output_file.exists()
        html_content = output_file.read_text(encoding="utf-8")
        assert "plotly" in html_content.lower()
        assert "Test Plot" in html_content

    def test_content_truncation(self, tmp_path: Path) -> None:
        """
        Verify content preview is truncated with ellipsis.

        Parameters
        ----------
        tmp_path : Path
            Pytest temporary directory fixture.
        """
        long_content = "A" * 300
        chunks = [
            {
                "document_name": "doc.md",
                "chunk_index": 0,
                "content": long_content,
                "metadata": {},
                "embedding": [random.gauss(0, 1) for _ in range(384)],
            }
            for _ in range(5)
        ]

        input_file = tmp_path / "embeddings.json"
        input_file.write_text(json.dumps(chunks), encoding="utf-8")
        output_file = tmp_path / "viz.html"

        with patch("rag_viz.app.task_inputs") as mock_inputs:
            _mock_inputs(mock_inputs, str(input_file), str(output_file))
            App().run()

        assert output_file.exists()
        html_content = output_file.read_text(encoding="utf-8")
        assert long_content not in html_content

    def test_query_overlay(self, tmp_path: Path) -> None:
        """
        Verify query point and retrieved chunks are overlaid on the plot.

        Parameters
        ----------
        tmp_path : Path
            Pytest temporary directory fixture.
        """
        chunks = _make_chunks()
        input_file = tmp_path / "embeddings.json"
        input_file.write_text(json.dumps(chunks), encoding="utf-8")

        # Create a SearchResponse JSON with query_embedding
        search_response = {
            "query": "What is chunk 0?",
            "results": [
                {
                    "chunk_id": "00000000-0000-0000-0000-000000000000",
                    "document_name": "doc-0.md",
                    "content": chunks[0]["content"],
                    "similarity_score": 0.95,
                    "metadata": {},
                },
                {
                    "chunk_id": "00000000-0000-0000-0000-000000000001",
                    "document_name": "doc-1.md",
                    "content": chunks[1]["content"],
                    "similarity_score": 0.85,
                    "metadata": {},
                },
            ],
            "total_results": 2,
            "embedding_time_ms": 10.0,
            "search_time_ms": 5.0,
            "query_embedding": [random.gauss(0, 1) for _ in range(384)],
        }

        query_file = tmp_path / "query.json"
        query_file.write_text(json.dumps(search_response), encoding="utf-8")
        output_file = tmp_path / "viz_query.html"

        with patch("rag_viz.app.task_inputs") as mock_inputs:
            _mock_inputs(mock_inputs, str(input_file), str(output_file), str(query_file))
            App().run()

        assert output_file.exists()
        html_content = output_file.read_text(encoding="utf-8")
        assert "Query" in html_content
        assert "Retrieved" in html_content

    def test_no_query_file_works(self, tmp_path: Path) -> None:
        """
        Verify the pipeline works without a query file (empty string).

        Parameters
        ----------
        tmp_path : Path
            Pytest temporary directory fixture.
        """
        chunks = _make_chunks(n=6)
        input_file = tmp_path / "embeddings.json"
        input_file.write_text(json.dumps(chunks), encoding="utf-8")
        output_file = tmp_path / "viz_no_query.html"

        with patch("rag_viz.app.task_inputs") as mock_inputs:
            _mock_inputs(mock_inputs, str(input_file), str(output_file), "")
            App().run()

        assert output_file.exists()
        html_content = output_file.read_text(encoding="utf-8")
        # No query trace or retrieved trace names should appear
        assert "Retrieved chunks" not in html_content
