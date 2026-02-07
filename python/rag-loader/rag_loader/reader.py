"""Document reader module for rag-loader."""

from pathlib import Path

SUPPORTED_EXTENSIONS = {".txt", ".md"}


def read_documents(input_dir: str) -> list[dict[str, object]]:
    """
    Read all supported text files from a directory.

    Reads ``.txt`` and ``.md`` files (non-recursive) and returns their
    content along with metadata.

    Parameters
    ----------
    input_dir : str
        Path to the directory containing documents.

    Returns
    -------
    list[dict[str, object]]
        List of dicts with keys ``document_name``, ``content``, ``metadata``.

    Raises
    ------
    FileNotFoundError
        If ``input_dir`` does not exist.
    NotADirectoryError
        If ``input_dir`` is not a directory.
    """
    path = Path(input_dir)
    if not path.exists():
        msg = f"Input directory does not exist: {input_dir}"
        raise FileNotFoundError(msg)
    if not path.is_dir():
        msg = f"Input path is not a directory: {input_dir}"
        raise NotADirectoryError(msg)

    documents: list[dict[str, object]] = []
    for file_path in sorted(path.iterdir()):
        if not file_path.is_file():
            continue
        if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        content = file_path.read_text(encoding="utf-8-sig")
        documents.append(
            {
                "document_name": file_path.name,
                "content": content,
                "metadata": {
                    "file_size": file_path.stat().st_size,
                    "extension": file_path.suffix.lower(),
                },
            }
        )

    return documents
