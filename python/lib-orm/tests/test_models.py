"""Tests for ORM models."""

from lib_orm.models import Base, DocumentChunk


def test_tablename() -> None:
    """Test that DocumentChunk maps to the correct table."""
    assert DocumentChunk.__tablename__ == "document_chunks"


def test_columns_exist() -> None:
    """
    Test that DocumentChunk has all expected columns.

    Checks the column names match the database schema.
    """
    column_names = {c.name for c in DocumentChunk.__table__.columns}
    expected = {
        "id",
        "document_name",
        "chunk_index",
        "content",
        "metadata",
        "embedding",
        "created_at",
    }
    assert column_names == expected


def test_unique_constraint() -> None:
    """
    Test that the unique constraint on document_name and chunk_index exists.

    Verifies the constraint name matches the database schema.
    """
    constraint_names = {c.name for c in DocumentChunk.__table__.constraints if c.name}
    assert "uq_document_chunk" in constraint_names


def test_base_registry() -> None:
    """Test that DocumentChunk is registered in the Base metadata."""
    assert "document_chunks" in Base.metadata.tables
