"""Tests for eval_loader."""

from pathlib import Path

import pytest

from eval_retriever.eval_loader import EvalSample, load_eval_samples

CSV_HEADER = "ID,Requête (Query),Correspondance (Content Match),Nom du Document,Chunk ID\n"


def _write_csv(path: Path, body: str) -> Path:
    """
    Write a CSV fixture with the standard eval-set header.

    Parameters
    ----------
    path : Path
        Destination file path.
    body : str
        CSV body rows (without header).

    Returns
    -------
    Path
        The path to the written file.
    """
    path.write_text(CSV_HEADER + body, encoding="utf-8")
    return path


def test_load_simple_csv(tmp_path: Path) -> None:
    """
    Load a minimal well-formed CSV and parse both rows.

    Parameters
    ----------
    tmp_path : Path
        Pytest temporary directory fixture.
    """
    csv_path = _write_csv(
        tmp_path / "eval.csv",
        '1,Qui est Pikachu ?,"""Pokemon electrique""",025-pikachu.md,0\n'
        '2,Qu\'est-ce que Bulbizarre ?,"""Pokemon plante""",001-bulbizarre.md,1\n',
    )

    samples = load_eval_samples(csv_path)

    assert len(samples) == 2
    assert isinstance(samples[0], EvalSample)
    assert samples[0].id == "1"
    assert samples[0].query == "Qui est Pikachu ?"
    assert samples[0].expected_document == "025-pikachu.md"
    assert samples[0].expected_chunk_id == "0"
    assert "Pokemon electrique" in samples[0].reference_passage
    assert samples[1].expected_document == "001-bulbizarre.md"


def test_load_skips_rows_missing_query_or_document(tmp_path: Path) -> None:
    """
    Skip rows with blank query or expected document silently.

    Parameters
    ----------
    tmp_path : Path
        Pytest temporary directory fixture.
    """
    csv_path = _write_csv(
        tmp_path / "eval.csv",
        '1,,"""x""",001-bulbizarre.md,0\n'
        '2,Qui est Pikachu ?,"""x""",,0\n'
        '3,Qui est Pikachu ?,"""x""",025-pikachu.md,0\n',
    )
    samples = load_eval_samples(csv_path)
    assert len(samples) == 1
    assert samples[0].id == "3"


def test_load_missing_file_raises(tmp_path: Path) -> None:
    """
    Raise ``FileNotFoundError`` when the CSV path does not exist.

    Parameters
    ----------
    tmp_path : Path
        Pytest temporary directory fixture.
    """
    with pytest.raises(FileNotFoundError, match="Eval CSV not found"):
        load_eval_samples(tmp_path / "does-not-exist.csv")


def test_load_missing_required_column_raises(tmp_path: Path) -> None:
    """
    Raise ``ValueError`` when required columns are missing from the CSV.

    Parameters
    ----------
    tmp_path : Path
        Pytest temporary directory fixture.
    """
    csv_path = tmp_path / "eval.csv"
    csv_path.write_text("ID,Query,Document\n1,hi,a.md\n", encoding="utf-8")
    with pytest.raises(ValueError, match="missing required columns"):
        load_eval_samples(csv_path)


def test_load_handles_utf8_bom(tmp_path: Path) -> None:
    """
    Parse a CSV that begins with a UTF-8 BOM without dropping rows.

    Parameters
    ----------
    tmp_path : Path
        Pytest temporary directory fixture.
    """
    csv_path = tmp_path / "eval.csv"
    csv_path.write_text(
        "\ufeff" + CSV_HEADER + '1,hi,"""x""",a.md,0\n',
        encoding="utf-8",
    )
    samples = load_eval_samples(csv_path)
    assert len(samples) == 1
    assert samples[0].query == "hi"


def test_eval_sample_is_frozen() -> None:
    """EvalSample instances are immutable."""
    sample = EvalSample(
        id="1",
        query="q",
        expected_document="a.md",
    )
    with pytest.raises(ValueError, match="frozen"):
        sample.query = "new"  # type: ignore[misc]
