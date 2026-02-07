"""Tests for embedding client."""

import pytest

from lib_embedding.embedding import EmbeddingClient

DIMENSION = 384


@pytest.fixture(scope="module")
def client() -> EmbeddingClient:
    """
    Return a shared EmbeddingClient instance.

    Returns
    -------
    EmbeddingClient
        A client loaded with all-MiniLM-L6-v2.
    """
    return EmbeddingClient("all-MiniLM-L6-v2")


def test_encode_single(client: EmbeddingClient) -> None:
    """
    Test encoding a single string returns one vector.

    Parameters
    ----------
    client : EmbeddingClient
        The embedding client fixture.
    """
    result = client.encode(["hello"])
    assert len(result) == 1
    assert len(result[0]) == DIMENSION
    assert all(isinstance(v, float) for v in result[0])


def test_encode_empty(client: EmbeddingClient) -> None:
    """
    Test encoding an empty list returns empty list.

    Parameters
    ----------
    client : EmbeddingClient
        The embedding client fixture.
    """
    result = client.encode([])
    assert result == []


def test_encode_batch(client: EmbeddingClient) -> None:
    """
    Test encoding multiple strings with small batch size.

    Parameters
    ----------
    client : EmbeddingClient
        The embedding client fixture.
    """
    texts = [f"text {i}" for i in range(10)]
    result = client.encode(texts, batch_size=3)
    assert len(result) == 10
    assert all(len(vec) == DIMENSION for vec in result)


def test_dimension(client: EmbeddingClient) -> None:
    """
    Test dimension property matches encode output.

    Parameters
    ----------
    client : EmbeddingClient
        The embedding client fixture.
    """
    assert client.dimension == DIMENSION
