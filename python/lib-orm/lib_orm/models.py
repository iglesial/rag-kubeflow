"""SQLAlchemy ORM models for RAG system."""

import uuid
from datetime import datetime
from typing import Any

from pgvector.sqlalchemy import Vector
from sqlalchemy import String, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    """Base class for all ORM models."""


class DocumentChunk(Base):
    """
    ORM model for the ``document_chunks`` table.

    Stores chunked document content with vector embeddings for similarity search.

    Attributes
    ----------
    id : uuid.UUID
        Primary key, auto-generated.
    document_name : str
        Name of the source document.
    chunk_index : int
        Index of this chunk within the document.
    content : str
        Text content of the chunk.
    metadata_ : dict[str, Any]
        Additional metadata as JSONB.
    embedding : Any
        384-dimensional vector embedding.
    created_at : datetime
        Timestamp of row creation.
    """

    __tablename__ = "document_chunks"
    __table_args__ = (UniqueConstraint("document_name", "chunk_index", name="uq_document_chunk"),)

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )
    document_name: Mapped[str] = mapped_column(String(512), nullable=False)
    chunk_index: Mapped[int] = mapped_column(nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSONB,
        nullable=False,
        server_default=text("'{}'::jsonb"),
    )
    embedding: Mapped[Any] = mapped_column(Vector(384), nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
