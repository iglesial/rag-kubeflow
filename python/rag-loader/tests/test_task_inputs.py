"""Tests for rag-loader task inputs."""

from rag_loader.task_inputs import TaskInputs, task_inputs


def test_task_inputs_defaults() -> None:
    """Test that TaskInputs has expected default values."""
    assert task_inputs.input_dir == "data/documents"
    assert task_inputs.output_dir == "data/chunks"
    assert task_inputs.chunk_size == 512
    assert task_inputs.chunk_overlap == 64


def test_task_inputs_is_instance() -> None:
    """Test that the module-level task_inputs is a TaskInputs instance."""
    assert isinstance(task_inputs, TaskInputs)
