"""Tests for rag-embedder batch writer."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from lib_schemas.schemas import ChunkWithEmbedding

from rag_embedder.writer import write_chunks


def _make_chunk(name: str, index: int) -> ChunkWithEmbedding:
    """
    Create a test ChunkWithEmbedding.

    Parameters
    ----------
    name : str
        Document name.
    index : int
        Chunk index.

    Returns
    -------
    ChunkWithEmbedding
        A test chunk with a dummy embedding.
    """
    return ChunkWithEmbedding(
        document_name=name,
        chunk_index=index,
        content=f"Content for {name} chunk {index}",
        metadata={},
        embedding=[0.1] * 384,
    )


@pytest.mark.asyncio
async def test_write_empty_list() -> None:
    """Test that writing an empty list returns 0."""
    session = AsyncMock()
    result = await write_chunks(session, [])
    assert result == 0
    session.flush.assert_not_awaited()


@pytest.mark.asyncio
async def test_write_inserts_new_chunks() -> None:
    """Test that new chunks are inserted via session.add."""
    session = AsyncMock()
    # scalar_one_or_none returns None -> new row
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    session.execute.return_value = mock_result

    chunks = [_make_chunk("doc.md", 0), _make_chunk("doc.md", 1)]
    count = await write_chunks(session, chunks)

    assert count == 2
    assert session.add.call_count == 2
    session.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_write_updates_existing_chunks() -> None:
    """Test that existing chunks are updated in place."""
    existing_row = MagicMock()
    existing_row.content = "old content"
    existing_row.metadata_ = {}
    existing_row.embedding = [0.0] * 384

    session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_row
    session.execute.return_value = mock_result

    chunks = [_make_chunk("doc.md", 0)]
    count = await write_chunks(session, chunks)

    assert count == 1
    assert existing_row.content == "Content for doc.md chunk 0"
    assert existing_row.embedding == [0.1] * 384
    # Should NOT call session.add for updates
    session.add.assert_not_called()
    session.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_write_five_chunks() -> None:
    """Test inserting 5 chunks returns count of 5."""
    session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    session.execute.return_value = mock_result

    chunks = [_make_chunk("doc.md", i) for i in range(5)]
    count = await write_chunks(session, chunks)

    assert count == 5
    assert session.add.call_count == 5


@pytest.mark.asyncio
async def test_write_mixed_insert_and_update() -> None:
    """Test a mix of new and existing chunks."""
    existing_row = MagicMock()
    existing_row.content = "old"
    existing_row.metadata_ = {}
    existing_row.embedding = [0.0] * 384

    session = AsyncMock()
    # First call: existing, second call: new
    result_existing = MagicMock()
    result_existing.scalar_one_or_none.return_value = existing_row
    result_new = MagicMock()
    result_new.scalar_one_or_none.return_value = None
    session.execute.side_effect = [result_existing, result_new]

    chunks = [_make_chunk("doc.md", 0), _make_chunk("doc.md", 1)]
    count = await write_chunks(session, chunks)

    assert count == 2
    assert session.add.call_count == 1  # only the new one
