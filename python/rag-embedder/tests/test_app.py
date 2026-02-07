"""Tests for rag-embedder App."""

import json
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from rag_embedder.app import App


@pytest.fixture
def chunks_dir(tmp_path: Path) -> Path:
    """
    Create a temp directory with sample chunk JSON.

    Parameters
    ----------
    tmp_path : Path
        Pytest temporary directory fixture.

    Returns
    -------
    Path
        Path to input directory with chunks.json.
    """
    input_dir = tmp_path / "chunks"
    input_dir.mkdir()
    chunks = [
        {
            "document_name": "test.md",
            "chunk_index": 0,
            "content": "Hello world",
            "metadata": {},
        },
        {
            "document_name": "test.md",
            "chunk_index": 1,
            "content": "Fluffy Cake is great",
            "metadata": {},
        },
    ]
    (input_dir / "chunks.json").write_text(json.dumps(chunks), encoding="utf-8")
    return input_dir


def test_run_embeds_and_saves(
    chunks_dir: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """
    Test that App.run() embeds chunks, saves to output dir, and writes to DB.

    Parameters
    ----------
    chunks_dir : Path
        Input directory with chunk JSON.
    tmp_path : Path
        Pytest temporary directory fixture.
    capsys : pytest.CaptureFixture[str]
        Pytest capture fixture.
    """
    output_dir = tmp_path / "embeddings"
    mock_write = AsyncMock(return_value=2)
    with (
        patch("rag_embedder.app.task_inputs") as mock_inputs,
        patch("rag_embedder.app.write_chunks", mock_write),
        patch("rag_embedder.app.get_async_session") as mock_session_ctx,
    ):
        mock_inputs.input_dir = str(chunks_dir)
        mock_inputs.output_dir = str(output_dir)
        mock_inputs.db_url = "postgresql+asyncpg://test:test@localhost/test"
        mock_inputs.embedding_model = "all-MiniLM-L6-v2"
        mock_inputs.batch_size = 32

        mock_session = AsyncMock()
        mock_session_ctx.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session_ctx.return_value.__aexit__ = AsyncMock(return_value=False)

        App().run()

    captured = capsys.readouterr()
    assert "Loaded 2 chunks" in captured.out
    assert "Embedded 2 chunks" in captured.out
    assert "Saved 2 embeddings" in captured.out
    assert "Wrote 2 rows to database" in captured.out

    embeddings_file = output_dir / "embeddings.json"
    assert embeddings_file.exists()
    data = json.loads(embeddings_file.read_text(encoding="utf-8"))
    assert len(data) == 2
    assert len(data[0]["embedding"]) == 384


def test_run_empty_input(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """
    Test that App.run() handles empty input directory.

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
    with patch("rag_embedder.app.task_inputs") as mock_inputs:
        mock_inputs.input_dir = str(input_dir)
        mock_inputs.output_dir = str(output_dir)
        mock_inputs.db_url = "postgresql+asyncpg://test:test@localhost/test"
        mock_inputs.embedding_model = "all-MiniLM-L6-v2"
        mock_inputs.batch_size = 32
        App().run()

    captured = capsys.readouterr()
    assert "Loaded 0 chunks" in captured.out
    assert "No chunks to embed" in captured.out


def test_run_db_failure_graceful(
    chunks_dir: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """
    Test that App.run() handles DB failure gracefully.

    Parameters
    ----------
    chunks_dir : Path
        Input directory with chunk JSON.
    tmp_path : Path
        Pytest temporary directory fixture.
    capsys : pytest.CaptureFixture[str]
        Pytest capture fixture.
    """
    output_dir = tmp_path / "embeddings"
    with (
        patch("rag_embedder.app.task_inputs") as mock_inputs,
        patch(
            "rag_embedder.app.get_async_session",
            side_effect=ConnectionRefusedError("Connection refused"),
        ),
    ):
        mock_inputs.input_dir = str(chunks_dir)
        mock_inputs.output_dir = str(output_dir)
        mock_inputs.db_url = "postgresql+asyncpg://test:test@localhost/test"
        mock_inputs.embedding_model = "all-MiniLM-L6-v2"
        mock_inputs.batch_size = 32
        App().run()

    captured = capsys.readouterr()
    assert "Saved 2 embeddings" in captured.out
    assert "DB write skipped:" in captured.out
