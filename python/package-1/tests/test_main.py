"""Tests for main module."""

from unittest.mock import patch

from package_1.app import App


def test_app_run(capsys: object) -> None:
    """Test that App.run prints the job run ID."""
    with patch("package_1.task_inputs.task_inputs") as mock_inputs:
        mock_inputs.job_run_id = 42
        app = App()
        app.run()
