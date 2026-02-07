"""Tests for rag-retriever task inputs."""

from rag_retriever.task_inputs import TaskInputs


def test_defaults() -> None:
    """Test that TaskInputs defaults are correct."""
    inputs = TaskInputs()
    assert inputs.host == "0.0.0.0"
    assert inputs.port == 8000
    assert inputs.db_url == "postgresql+asyncpg://rag:rag@localhost:5432/rag"
    assert inputs.embedding_model == "all-MiniLM-L6-v2"
    assert inputs.top_k == 5
