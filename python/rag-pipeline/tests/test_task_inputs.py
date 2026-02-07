"""Tests for rag-pipeline task inputs."""

from rag_pipeline.task_inputs import TaskInputs


def test_defaults() -> None:
    """Test that TaskInputs defaults are correct."""
    inputs = TaskInputs()
    assert inputs.pipeline_name == "rag-ingestion"
    assert inputs.input_dir == "data/documents"
    assert inputs.kubeflow_host == "http://localhost:8080"
    assert inputs.compile_only is False
