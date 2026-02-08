"""Tests for rag-pipeline App."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from rag_pipeline.app import App


def test_run_compile_only(capsys: pytest.CaptureFixture[str], tmp_path: Path) -> None:
    """
    Test that App.run() compiles YAML when compile_only is True.

    Parameters
    ----------
    capsys : pytest.CaptureFixture[str]
        Pytest capture fixture.
    tmp_path : Path
        Pytest temporary directory fixture.
    """
    yaml_path = str(tmp_path / "pipeline.yaml")
    with (
        patch("rag_pipeline.app.task_inputs") as mock_inputs,
        patch("rag_pipeline.app.PIPELINE_YAML", yaml_path),
    ):
        mock_inputs.pipeline_name = "rag-ingestion"
        mock_inputs.input_dir = "data/documents"
        mock_inputs.kubeflow_host = "http://localhost:8080"
        mock_inputs.compile_only = True
        mock_inputs.chunk_size = 512
        mock_inputs.chunk_overlap = 64
        mock_inputs.db_url = "postgresql+asyncpg://rag:rag@localhost:5432/rag"
        mock_inputs.embedding_model = "all-MiniLM-L6-v2"
        mock_inputs.batch_size = 32
        App().run()

    captured = capsys.readouterr()
    assert "Pipeline name:" in captured.out
    assert "Compiled pipeline to" in captured.out
    assert Path(yaml_path).exists()


def test_run_submit_fails_gracefully(capsys: pytest.CaptureFixture[str], tmp_path: Path) -> None:
    """
    Test that App.run() handles KFP submission failure gracefully.

    Parameters
    ----------
    capsys : pytest.CaptureFixture[str]
        Pytest capture fixture.
    tmp_path : Path
        Pytest temporary directory fixture.
    """
    yaml_path = str(tmp_path / "pipeline.yaml")
    mock_client_cls = MagicMock(side_effect=ConnectionError("no KFP"))
    with (
        patch("rag_pipeline.app.task_inputs") as mock_inputs,
        patch("rag_pipeline.app.PIPELINE_YAML", yaml_path),
        patch.dict("sys.modules", {"kfp.client": MagicMock(Client=mock_client_cls)}),
    ):
        mock_inputs.pipeline_name = "rag-ingestion"
        mock_inputs.input_dir = "data/documents"
        mock_inputs.kubeflow_host = "http://localhost:8080"
        mock_inputs.compile_only = False
        mock_inputs.chunk_size = 512
        mock_inputs.chunk_overlap = 64
        mock_inputs.db_url = "postgresql+asyncpg://rag:rag@localhost:5432/rag"
        mock_inputs.embedding_model = "all-MiniLM-L6-v2"
        mock_inputs.batch_size = 32
        App().run()

    captured = capsys.readouterr()
    assert "Compiled pipeline to" in captured.out
    assert "Pipeline submission failed:" in captured.out
