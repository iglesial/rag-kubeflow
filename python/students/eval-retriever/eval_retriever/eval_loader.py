"""Load ground-truth eval samples from a CSV file."""

import csv
from pathlib import Path

from pydantic import BaseModel, ConfigDict

# CSV column names as they appear in data/eval/eval_set.csv.
COL_ID = "ID"
COL_QUERY = "Requête (Query)"
COL_CORRESPONDENCE = "Correspondance (Content Match)"
COL_DOCUMENT = "Nom du Document"
COL_CHUNK_ID = "Chunk ID"

_REQUIRED_COLUMNS = (COL_ID, COL_QUERY, COL_DOCUMENT)


class EvalSample(BaseModel):
    """
    A single ground-truth sample from the eval set.

    Attributes
    ----------
    id : str
        Row identifier from the CSV.
    query : str
        The search query text.
    expected_document : str
        Filename of the document the query is expected to retrieve.
    expected_chunk_id : str | None
        Chunk index within the expected document, if provided.
    reference_passage : str
        The exact passage cited in the eval set (informational only,
        not used for scoring).
    """

    model_config = ConfigDict(frozen=True)

    id: str
    query: str
    expected_document: str
    expected_chunk_id: str | None = None
    reference_passage: str = ""


def load_eval_samples(csv_path: str | Path) -> list[EvalSample]:
    """
    Load eval samples from a CSV file on disk.

    The CSV is expected to have the columns ``ID``, ``Requête (Query)``,
    ``Correspondance (Content Match)``, ``Nom du Document``, and ``Chunk ID``.
    Empty rows and rows missing the query or expected document are skipped.

    Parameters
    ----------
    csv_path : str | Path
        Filesystem path to the eval CSV.

    Returns
    -------
    list[EvalSample]
        Parsed eval samples in the order they appear in the file.

    Raises
    ------
    FileNotFoundError
        If the CSV file does not exist.
    ValueError
        If the CSV is missing any of the required columns.
    """
    path = Path(csv_path)
    if not path.exists():
        msg = f"Eval CSV not found: {csv_path}"
        raise FileNotFoundError(msg)

    samples: list[EvalSample] = []
    with path.open(encoding="utf-8-sig", newline="") as fp:
        reader = csv.DictReader(fp)
        if reader.fieldnames is None:
            msg = f"Eval CSV has no header row: {csv_path}"
            raise ValueError(msg)
        missing = [col for col in _REQUIRED_COLUMNS if col not in reader.fieldnames]
        if missing:
            msg = f"Eval CSV {csv_path} is missing required columns: {missing}"
            raise ValueError(msg)

        for row in reader:
            query = (row.get(COL_QUERY) or "").strip()
            expected_document = (row.get(COL_DOCUMENT) or "").strip()
            if not query or not expected_document:
                continue
            samples.append(
                EvalSample(
                    id=(row.get(COL_ID) or "").strip(),
                    query=query,
                    expected_document=expected_document,
                    expected_chunk_id=(row.get(COL_CHUNK_ID) or "").strip() or None,
                    reference_passage=(row.get(COL_CORRESPONDENCE) or "").strip(),
                )
            )

    return samples
