"""Tests for rag-embedder task inputs."""

from rag_embedder.task_inputs import TaskInputs, task_inputs


def test_task_inputs_defaults() -> None:
    """Test that TaskInputs has expected default values."""
    assert task_inputs.input_dir == "data/chunks"
    assert task_inputs.output_dir == "data/embeddings"
    assert task_inputs.db_url == "postgresql+asyncpg://rag:rag@localhost:5432/rag"
    assert task_inputs.embedding_model == "all-MiniLM-L6-v2"
    assert task_inputs.batch_size == 32


def test_task_inputs_is_instance() -> None:
    """Test that the module-level task_inputs is a TaskInputs instance."""
    assert isinstance(task_inputs, TaskInputs)
