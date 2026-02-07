"""Batch writer for inserting chunk embeddings into pgvector."""

from lib_orm.models import DocumentChunk
from lib_schemas.schemas import ChunkWithEmbedding
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def write_chunks(session: AsyncSession, chunks: list[ChunkWithEmbedding]) -> int:
    """
    Batch-insert chunks with embeddings into the database.

    Uses upsert semantics: existing rows matching ``(document_name, chunk_index)``
    are updated; new rows are inserted.

    Parameters
    ----------
    session : AsyncSession
        Active async database session.
    chunks : list[ChunkWithEmbedding]
        Chunks with embeddings to write.

    Returns
    -------
    int
        Number of rows affected (inserted or updated).
    """
    if not chunks:
        return 0

    count = 0
    for chunk in chunks:
        result = await session.execute(
            select(DocumentChunk).where(
                DocumentChunk.document_name == chunk.document_name,
                DocumentChunk.chunk_index == chunk.chunk_index,
            )
        )
        existing = result.scalar_one_or_none()

        if existing is not None:
            existing.content = chunk.content
            existing.metadata_ = chunk.metadata
            existing.embedding = chunk.embedding
        else:
            session.add(
                DocumentChunk(
                    document_name=chunk.document_name,
                    chunk_index=chunk.chunk_index,
                    content=chunk.content,
                    metadata_=chunk.metadata,
                    embedding=chunk.embedding,
                )
            )
        count += 1

    await session.flush()
    return count
