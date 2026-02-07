"""Tests for rag-retriever App."""

from unittest.mock import patch

import pytest

from rag_retriever.app import App


def test_run_starts_uvicorn(capsys: pytest.CaptureFixture[str]) -> None:
    """
    Test that App.run() prints config and calls uvicorn.run.

    Parameters
    ----------
    capsys : pytest.CaptureFixture[str]
        Pytest capture fixture.
    """
    with (
        patch("rag_retriever.app.task_inputs") as mock_inputs,
        patch("rag_retriever.app.uvicorn") as mock_uvicorn,
    ):
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

    mock_uvicorn.run.assert_called_once_with(
        "rag_retriever.api:create_app",
        host="0.0.0.0",
        port=8000,
        factory=True,
    )
