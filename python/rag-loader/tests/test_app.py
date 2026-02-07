"""Tests for rag-loader App."""

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from rag_loader.app import App


@pytest.fixture
def sample_dir(tmp_path: Path) -> Path:
    """
    Create a temp directory with sample documents.

    Parameters
    ----------
    tmp_path : Path
        Pytest temporary directory fixture.

    Returns
    -------
    Path
        Path to the input directory containing sample files.
    """
    input_dir = tmp_path / "docs"
    input_dir.mkdir()
    (input_dir / "a.md").write_text("Hello world.", encoding="utf-8")
    (input_dir / "b.txt").write_text("Another document.", encoding="utf-8")
    return input_dir


def test_run_reads_and_chunks(
    sample_dir: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """
    Test that App.run() reads documents, chunks them, and writes JSON output.

    Parameters
    ----------
    sample_dir : Path
        Input directory with sample documents.
    tmp_path : Path
        Pytest temporary directory fixture.
    capsys : pytest.CaptureFixture[str]
        Pytest capture fixture.
    """
    output_dir = tmp_path / "out"
    with patch("rag_loader.app.task_inputs") as mock_inputs:
        mock_inputs.input_dir = str(sample_dir)
        mock_inputs.output_dir = str(output_dir)
        mock_inputs.chunk_size = 512
        mock_inputs.chunk_overlap = 64
        App().run()

    captured = capsys.readouterr()
    assert "Read 2 documents" in captured.out
    assert "Generated" in captured.out
    assert "Saved chunks to" in captured.out

    chunks_file = output_dir / "chunks.json"
    assert chunks_file.exists()
    data = json.loads(chunks_file.read_text(encoding="utf-8"))
    assert len(data) >= 2
    assert data[0]["document_name"] == "a.md"
    assert "content" in data[0]


def test_run_empty_dir(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """
    Test that App.run() handles an empty input directory.

    Parameters
    ----------
    tmp_path : Path
        Pytest temporary directory fixture.
    capsys : pytest.CaptureFixture[str]
        Pytest capture fixture.
    """
    input_dir = tmp_path / "empty"
    input_dir.mkdir()
    output_dir = tmp_path / "out"
    with patch("rag_loader.app.task_inputs") as mock_inputs:
        mock_inputs.input_dir = str(input_dir)
        mock_inputs.output_dir = str(output_dir)
        mock_inputs.chunk_size = 512
        mock_inputs.chunk_overlap = 64
        App().run()

    captured = capsys.readouterr()
    assert "Read 0 documents" in captured.out
    assert "Generated 0 chunks" in captured.out

    data = json.loads((output_dir / "chunks.json").read_text(encoding="utf-8"))
    assert data == []
