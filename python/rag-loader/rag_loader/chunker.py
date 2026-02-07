"""Recursive character text splitter for rag-loader."""

SEPARATORS = ["\n\n", "\n", ". ", " ", ""]


def chunk_text(text: str, chunk_size: int = 512, chunk_overlap: int = 64) -> list[str]:
    """
    Split text into overlapping chunks using a recursive character strategy.

    Tries separators in order (paragraph, newline, sentence, word, character)
    and falls back to the next separator when a segment exceeds ``chunk_size``.

    Parameters
    ----------
    text : str
        The input text to split.
    chunk_size : int
        Maximum number of characters per chunk.
    chunk_overlap : int
        Number of overlapping characters between consecutive chunks.

    Returns
    -------
    list[str]
        List of text chunks.

    Raises
    ------
    ValueError
        If ``chunk_overlap`` is greater than or equal to ``chunk_size``.
    """
    if chunk_overlap >= chunk_size:
        msg = f"chunk_overlap ({chunk_overlap}) must be less than chunk_size ({chunk_size})"
        raise ValueError(msg)
    if not text.strip():
        return []
    return _merge_with_overlap(_split_recursive(text, chunk_size, 0), chunk_size, chunk_overlap)


def _split_recursive(text: str, chunk_size: int, sep_idx: int) -> list[str]:
    """
    Recursively split text using the separator hierarchy.

    Parameters
    ----------
    text : str
        Text to split.
    chunk_size : int
        Maximum chunk size.
    sep_idx : int
        Current index into the ``SEPARATORS`` list.

    Returns
    -------
    list[str]
        List of text segments.
    """
    if len(text) <= chunk_size:
        return [text]

    if sep_idx >= len(SEPARATORS):
        return [text]

    sep = SEPARATORS[sep_idx]

    if sep == "":
        return [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]

    parts = text.split(sep)
    if len(parts) == 1:
        return _split_recursive(text, chunk_size, sep_idx + 1)

    # Re-attach separator to each part (except the last) for ". " splits
    if sep == ". ":
        parts = [p + "." if i < len(parts) - 1 else p for i, p in enumerate(parts)]
    segments: list[str] = []
    for part in parts:
        stripped = part.strip()
        if not stripped:
            continue
        if len(stripped) <= chunk_size:
            segments.append(stripped)
        else:
            segments.extend(_split_recursive(stripped, chunk_size, sep_idx + 1))

    return segments


def _merge_with_overlap(segments: list[str], chunk_size: int, chunk_overlap: int) -> list[str]:
    """
    Merge small segments into chunks and add overlap between them.

    Parameters
    ----------
    segments : list[str]
        Text segments to merge.
    chunk_size : int
        Maximum chunk size.
    chunk_overlap : int
        Target overlap between consecutive chunks.

    Returns
    -------
    list[str]
        Merged chunks with overlap.
    """
    if not segments:
        return []

    chunks: list[str] = []
    current = segments[0]

    for segment in segments[1:]:
        candidate = current + " " + segment
        if len(candidate) <= chunk_size:
            current = candidate
        else:
            chunks.append(current)
            # Build overlap from the tail of the previous chunk
            overlap = current[-chunk_overlap:] if chunk_overlap > 0 else ""
            if overlap and len(overlap) + 1 + len(segment) <= chunk_size:
                current = overlap.lstrip() + " " + segment
            else:
                current = segment

    chunks.append(current)
    return chunks
