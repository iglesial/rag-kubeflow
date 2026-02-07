"""Tests for rag-embedder App."""

import pytest

from rag_embedder.app import App


def test_run_prints_config(capsys: pytest.CaptureFixture[str]) -> None:
    """
    Test that App.run() prints configuration info.

    Parameters
    ----------
    capsys : pytest.CaptureFixture[str]
        Pytest capture fixture.
    """
    App().run()
    captured = capsys.readouterr()
    assert "Input directory:" in captured.out
    assert "Database URL:" in captured.out
    assert "Embedding model:" in captured.out
    assert "Batch size:" in captured.out
    assert "rag-embedder: OK" in captured.out
