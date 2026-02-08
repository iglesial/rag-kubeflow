"""Tests for rag-pipeline App."""

from unittest.mock import patch

import pytest

from rag_pipeline.app import App


def test_run_prints_config(capsys: pytest.CaptureFixture[str]) -> None:
    """
    Test that App.run() prints configuration values.

    Parameters
    ----------
    capsys : pytest.CaptureFixture[str]
        Pytest capture fixture.
    """
    with patch("rag_pipeline.app.task_inputs") as mock_inputs:
        mock_inputs.pipeline_name = "rag-ingestion"
        mock_inputs.input_dir = "data/documents"
        mock_inputs.kubeflow_host = "http://localhost:8080"
        mock_inputs.compile_only = False
        App().run()

    captured = capsys.readouterr()
    assert "Pipeline name:" in captured.out
    assert "Input directory:" in captured.out
    assert "Kubeflow host:" in captured.out
    assert "Compile only:" in captured.out
