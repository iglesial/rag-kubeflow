"""Tests for lib-embedding App diagnostics."""

import pytest

from lib_embedding.app import App


@pytest.fixture(scope="module")
def app() -> App:
    """
    Return a shared App instance.

    Returns
    -------
    App
        An App instance for diagnostics.
    """
    return App()


def test_run_prints_model_info(app: App, capsys: pytest.CaptureFixture[str]) -> None:
    """
    Test that App.run() prints model name and dimension.

    Parameters
    ----------
    app : App
        The app fixture.
    capsys : pytest.CaptureFixture[str]
        Pytest capture fixture.
    """
    app.run()
    captured = capsys.readouterr()
    assert "all-MiniLM-L6-v2" in captured.out
    assert "384 dims" in captured.out
