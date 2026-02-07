"""Tests for lib-orm App diagnostics."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest

from lib_orm.app import App


def test_run_db_ok(capsys: pytest.CaptureFixture[str]) -> None:
    """
    Test that App.run() prints OK when DB is reachable.

    Parameters
    ----------
    capsys : pytest.CaptureFixture[str]
        Pytest capture fixture.
    """

    @asynccontextmanager
    async def _fake_connect() -> AsyncGenerator[Any]:
        """
        Yield a mock connection.

        Yields
        ------
        Any
            A mock connection object.
        """
        yield AsyncMock()

    mock_engine = AsyncMock()
    mock_engine.connect = _fake_connect
    mock_engine.dispose = AsyncMock()

    with patch("lib_orm.app.get_async_engine", return_value=mock_engine):
        app = App()
        app.run()

    captured = capsys.readouterr()
    assert "DB connection: OK" in captured.out


def test_run_db_failed(capsys: pytest.CaptureFixture[str]) -> None:
    """
    Test that App.run() prints FAILED when DB is unreachable.

    Parameters
    ----------
    capsys : pytest.CaptureFixture[str]
        Pytest capture fixture.
    """

    @asynccontextmanager
    async def _failing_connect() -> AsyncGenerator[Any]:
        """
        Raise ConnectionRefusedError before yielding.

        Yields
        ------
        Any
            Never yields; raises before reaching yield.
        """
        raise ConnectionRefusedError("Connection refused")
        yield  # pragma: no cover

    mock_engine = AsyncMock()
    mock_engine.connect = _failing_connect
    mock_engine.dispose = AsyncMock()

    with patch("lib_orm.app.get_async_engine", return_value=mock_engine):
        app = App()
        app.run()

    captured = capsys.readouterr()
    assert "DB connection: FAILED" in captured.out
    assert "Connection refused" in captured.out
