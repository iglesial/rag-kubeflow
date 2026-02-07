"""Tests for rag-retriever App."""

from unittest.mock import patch

import pytest

from rag_retriever.app import App


def test_run_prints_config(capsys: pytest.CaptureFixture[str]) -> None:
    """
    Test that App.run() prints configuration values.

    Parameters
    ----------
    capsys : pytest.CaptureFixture[str]
        Pytest capture fixture.
    """
    with patch("rag_retriever.app.task_inputs") as mock_inputs:
        mock_inputs.host = "0.0.0.0"
        mock_inputs.port = 8000
        mock_inputs.db_url = "postgresql+asyncpg://rag:rag@localhost:5432/rag"
        mock_inputs.embedding_model = "all-MiniLM-L6-v2"
        mock_inputs.top_k = 5
        App().run()

    captured = capsys.readouterr()
    assert "Host:" in captured.out
    assert "Port:" in captured.out
    assert "Database URL:" in captured.out
    assert "Embedding model:" in captured.out
    assert "Default top_k:" in captured.out
