"""Pydantic schemas for RAG system data exchange."""

import uuid

from pydantic import BaseModel, Field


class ChunkInput(BaseModel):
    """
    Input schema for a document chunk.

    Attributes
    ----------
    document_name : str
        Name of the source document.
    chunk_index : int
        Index of this chunk within the document.
    content : str
        Text content of the chunk.
    metadata : dict[str, str]
        Additional metadata (e.g. file size, extension).
    """

    document_name: str
    chunk_index: int
    content: str
    metadata: dict[str, str] = Field(default_factory=dict)


class ChunkWithEmbedding(ChunkInput):
    """
    A document chunk with its embedding vector.

    Attributes
    ----------
    document_name : str
        Name of the source document.
    chunk_index : int
        Index of this chunk within the document.
    content : str
        Text content of the chunk.
    metadata : dict[str, str]
        Additional metadata.
    embedding : list[float]
        Embedding vector for this chunk.
    """

    embedding: list[float]


class SearchRequest(BaseModel):
    """
    Request body for the search endpoint.

    Attributes
    ----------
    query : str
        Search query text (minimum 1 character).
    top_k : int
        Maximum number of results to return (1-50).
    similarity_threshold : float
        Minimum similarity score for results (0.0-1.0).
    """

    query: str = Field(min_length=1)
    top_k: int = Field(default=5, ge=1, le=50)
    similarity_threshold: float = Field(default=0.0, ge=0.0, le=1.0)


class SearchResult(BaseModel):
    """
    A single search result.

    Attributes
    ----------
    chunk_id : uuid.UUID
        ID of the matching chunk.
    document_name : str
        Name of the source document.
    content : str
        Text content of the matching chunk.
    similarity_score : float
        Cosine similarity score.
    metadata : dict[str, str]
        Chunk metadata.
    """

    chunk_id: uuid.UUID
    document_name: str
    content: str
    similarity_score: float
    metadata: dict[str, str] = Field(default_factory=dict)


class SearchResponse(BaseModel):
    """
    Response from the search endpoint.

    Attributes
    ----------
    query : str
        The original search query.
    results : list[SearchResult]
        Ranked list of search results.
    total_results : int
        Number of results returned.
    embedding_time_ms : float
        Time spent embedding the query in milliseconds.
    search_time_ms : float
        Time spent searching the database in milliseconds.
    """

    query: str
    results: list[SearchResult]
    total_results: int
    embedding_time_ms: float
    search_time_ms: float


class StatsResponse(BaseModel):
    """
    Response from the stats endpoint.

    Attributes
    ----------
    total_documents : int
        Number of unique documents in the database.
    total_chunks : int
        Total number of chunks across all documents.
    embedding_dimension : int
        Dimension of the embedding vectors.
    model_name : str
        Name of the embedding model.
    """

    total_documents: int
    total_chunks: int
    embedding_dimension: int
    model_name: str
