"""Tests for Pydantic schemas."""

import uuid

import pytest
from pydantic import ValidationError

from lib_schemas.schemas import (
    ChunkInput,
    ChunkWithEmbedding,
    SearchRequest,
    SearchResponse,
    SearchResult,
    StatsResponse,
)


class TestChunkInput:
    """Tests for ChunkInput schema."""

    def test_valid(self) -> None:
        """Test creating a valid ChunkInput."""
        chunk = ChunkInput(
            document_name="doc.md",
            chunk_index=0,
            content="Hello world",
        )
        assert chunk.document_name == "doc.md"
        assert chunk.chunk_index == 0
        assert chunk.content == "Hello world"
        assert chunk.metadata == {}

    def test_with_metadata(self) -> None:
        """Test creating a ChunkInput with metadata."""
        chunk = ChunkInput(
            document_name="doc.md",
            chunk_index=1,
            content="text",
            metadata={"size": "1024", "ext": ".md"},
        )
        assert chunk.metadata == {"size": "1024", "ext": ".md"}

    def test_missing_document_name(self) -> None:
        """Test that missing document_name raises ValidationError."""
        with pytest.raises(ValidationError):
            ChunkInput(chunk_index=0, content="text")  # type: ignore[call-arg]


class TestChunkWithEmbedding:
    """Tests for ChunkWithEmbedding schema."""

    def test_valid(self) -> None:
        """Test creating a valid ChunkWithEmbedding."""
        chunk = ChunkWithEmbedding(
            document_name="doc.md",
            chunk_index=0,
            content="text",
            embedding=[0.1, 0.2, 0.3],
        )
        assert chunk.embedding == [0.1, 0.2, 0.3]

    def test_missing_embedding(self) -> None:
        """Test that missing embedding raises ValidationError."""
        with pytest.raises(ValidationError):
            ChunkWithEmbedding(  # type: ignore[call-arg]
                document_name="doc.md",
                chunk_index=0,
                content="text",
            )


class TestSearchRequest:
    """Tests for SearchRequest schema."""

    def test_defaults(self) -> None:
        """Test that SearchRequest uses correct defaults."""
        req = SearchRequest(query="hello")
        assert req.query == "hello"
        assert req.top_k == 5
        assert req.similarity_threshold == 0.0

    def test_custom_values(self) -> None:
        """Test creating a SearchRequest with custom values."""
        req = SearchRequest(query="test", top_k=10, similarity_threshold=0.5)
        assert req.top_k == 10
        assert req.similarity_threshold == 0.5

    def test_empty_query(self) -> None:
        """Test that empty query raises ValidationError."""
        with pytest.raises(ValidationError):
            SearchRequest(query="")

    def test_top_k_zero(self) -> None:
        """Test that top_k=0 raises ValidationError."""
        with pytest.raises(ValidationError):
            SearchRequest(query="hello", top_k=0)

    def test_top_k_too_large(self) -> None:
        """Test that top_k>50 raises ValidationError."""
        with pytest.raises(ValidationError):
            SearchRequest(query="hello", top_k=51)

    def test_threshold_out_of_range(self) -> None:
        """Test that similarity_threshold>1.0 raises ValidationError."""
        with pytest.raises(ValidationError):
            SearchRequest(query="hello", similarity_threshold=1.5)


class TestSearchResult:
    """Tests for SearchResult schema."""

    def test_valid(self) -> None:
        """Test creating a valid SearchResult."""
        result = SearchResult(
            chunk_id=uuid.uuid4(),
            document_name="doc.md",
            content="text",
            similarity_score=0.85,
        )
        assert result.similarity_score == 0.85
        assert result.metadata == {}

    def test_round_trip(self) -> None:
        """Test JSON serialization round-trip."""
        original = SearchResult(
            chunk_id=uuid.uuid4(),
            document_name="doc.md",
            content="text",
            similarity_score=0.9,
            metadata={"ext": ".md"},
        )
        json_str = original.model_dump_json()
        restored = SearchResult.model_validate_json(json_str)
        assert restored == original


class TestSearchResponse:
    """Tests for SearchResponse schema."""

    def test_valid(self) -> None:
        """Test creating a valid SearchResponse."""
        response = SearchResponse(
            query="hello",
            results=[],
            total_results=0,
            embedding_time_ms=1.5,
            search_time_ms=3.2,
        )
        assert response.total_results == 0
        assert response.results == []

    def test_with_results(self) -> None:
        """Test SearchResponse with populated results."""
        result = SearchResult(
            chunk_id=uuid.uuid4(),
            document_name="doc.md",
            content="text",
            similarity_score=0.85,
        )
        response = SearchResponse(
            query="test",
            results=[result],
            total_results=1,
            embedding_time_ms=2.0,
            search_time_ms=5.0,
        )
        assert len(response.results) == 1
        assert response.results[0].document_name == "doc.md"


class TestStatsResponse:
    """Tests for StatsResponse schema."""

    def test_valid(self) -> None:
        """Test creating a valid StatsResponse."""
        stats = StatsResponse(
            total_documents=3,
            total_chunks=42,
            embedding_dimension=384,
            model_name="all-MiniLM-L6-v2",
        )
        assert stats.total_documents == 3
        assert stats.total_chunks == 42
        assert stats.embedding_dimension == 384
        assert stats.model_name == "all-MiniLM-L6-v2"
