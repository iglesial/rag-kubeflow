"""Tests for rag-loader document reader."""

from pathlib import Path

import pytest

from rag_loader.reader import read_documents


@pytest.fixture
def docs_dir(tmp_path: Path) -> Path:
    """
    Create a temp directory with sample documents.

    Parameters
    ----------
    tmp_path : Path
        Pytest temporary directory fixture.

    Returns
    -------
    Path
        Path to the temp directory containing sample files.
    """
    (tmp_path / "doc1.md").write_text("# Hello\n\nWorld", encoding="utf-8")
    (tmp_path / "doc2.txt").write_text("Plain text content", encoding="utf-8")
    (tmp_path / "image.png").write_bytes(b"\x89PNG\r\n")
    (tmp_path / "notes.pdf").write_bytes(b"%PDF-1.4")
    return tmp_path


def test_reads_md_and_txt(docs_dir: Path) -> None:
    """
    Test that only .md and .txt files are read.

    Parameters
    ----------
    docs_dir : Path
        Temp directory with mixed file types.
    """
    result = read_documents(str(docs_dir))
    names = [d["document_name"] for d in result]
    assert "doc1.md" in names
    assert "doc2.txt" in names
    assert len(result) == 2


def test_ignores_non_text_files(docs_dir: Path) -> None:
    """
    Test that non-text files are ignored.

    Parameters
    ----------
    docs_dir : Path
        Temp directory with mixed file types.
    """
    result = read_documents(str(docs_dir))
    names = [d["document_name"] for d in result]
    assert "image.png" not in names
    assert "notes.pdf" not in names


def test_document_content(docs_dir: Path) -> None:
    """
    Test that document content is read correctly.

    Parameters
    ----------
    docs_dir : Path
        Temp directory with sample documents.
    """
    result = read_documents(str(docs_dir))
    by_name = {d["document_name"]: d for d in result}
    assert by_name["doc1.md"]["content"] == "# Hello\n\nWorld"
    assert by_name["doc2.txt"]["content"] == "Plain text content"


def test_document_metadata(docs_dir: Path) -> None:
    """
    Test that metadata includes file size and extension.

    Parameters
    ----------
    docs_dir : Path
        Temp directory with sample documents.
    """
    result = read_documents(str(docs_dir))
    by_name = {d["document_name"]: d for d in result}
    meta = by_name["doc1.md"]["metadata"]
    assert isinstance(meta, dict)
    assert meta["extension"] == ".md"
    assert isinstance(meta["file_size"], int)
    assert meta["file_size"] > 0


def test_empty_directory(tmp_path: Path) -> None:
    """
    Test that an empty directory returns an empty list.

    Parameters
    ----------
    tmp_path : Path
        Pytest temporary directory fixture.
    """
    result = read_documents(str(tmp_path))
    assert result == []


def test_nonexistent_directory() -> None:
    """Test that a non-existent directory raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError, match="does not exist"):
        read_documents("/no/such/path")


def test_utf8_bom(tmp_path: Path) -> None:
    """
    Test that a file with UTF-8 BOM is read correctly.

    Parameters
    ----------
    tmp_path : Path
        Pytest temporary directory fixture.
    """
    bom = b"\xef\xbb\xbf"
    (tmp_path / "bom.txt").write_bytes(bom + b"BOM content")
    result = read_documents(str(tmp_path))
    assert len(result) == 1
    assert result[0]["content"] == "BOM content"


def test_two_md_files(tmp_path: Path) -> None:
    """
    Test directory with exactly 2 markdown files.

    Parameters
    ----------
    tmp_path : Path
        Pytest temporary directory fixture.
    """
    (tmp_path / "a.md").write_text("Alpha", encoding="utf-8")
    (tmp_path / "b.md").write_text("Beta", encoding="utf-8")
    result = read_documents(str(tmp_path))
    assert len(result) == 2
