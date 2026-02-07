"""Tests for rag-loader App."""

import pytest

from rag_loader.app import App


@pytest.fixture
def app() -> App:
    """
    Create an App instance for testing.

    Returns
    -------
    App
        A new App instance.
    """
    return App()


def test_run_prints_config(app: App, capsys: pytest.CaptureFixture[str]) -> None:
    """
    Test that App.run() prints configuration info.

    Parameters
    ----------
    app : App
        The App instance under test.
    capsys : pytest.CaptureFixture[str]
        Pytest capture fixture.
    """
    app.run()
    captured = capsys.readouterr()
    assert "Input directory:" in captured.out
    assert "Output directory:" in captured.out
    assert "Chunk size:" in captured.out
    assert "Chunk overlap:" in captured.out
    assert "rag-loader: OK" in captured.out
