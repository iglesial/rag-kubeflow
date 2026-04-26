"""Tests for the retriever HTTP client."""

import httpx
import pytest

from eval_retriever.retriever_client import RetrieverClient


def _make_client_with_handler(handler: httpx.MockTransport) -> RetrieverClient:
    """
    Build a RetrieverClient whose internal httpx.Client uses the mock transport.

    Parameters
    ----------
    handler : httpx.MockTransport
        The mock transport to inject.

    Returns
    -------
    RetrieverClient
        A client wired to the mock transport.
    """
    client = RetrieverClient("http://test")
    client._client.close()  # discard the real client  # noqa: SLF001
    client._client = httpx.Client(base_url="http://test", transport=handler)  # noqa: SLF001
    return client


def test_search_returns_ordered_document_names() -> None:
    """Search returns document_names in the order the retriever sends them."""

    def handler(request: httpx.Request) -> httpx.Response:
        """
        Return a canned payload for any /search POST.

        Parameters
        ----------
        request : httpx.Request
            The intercepted HTTP request.

        Returns
        -------
        httpx.Response
            A fake search response with three hits.
        """
        assert request.url.path == "/search"
        return httpx.Response(
            200,
            json={
                "query": "dummy",
                "total_results": 3,
                "embedding_time_ms": 1.0,
                "search_time_ms": 1.0,
                "results": [
                    {
                        "chunk_id": "11111111-1111-1111-1111-111111111111",
                        "document_name": "025-pikachu.md",
                        "content": "...",
                        "similarity_score": 0.9,
                    },
                    {
                        "chunk_id": "22222222-2222-2222-2222-222222222222",
                        "document_name": "001-bulbizarre.md",
                        "content": "...",
                        "similarity_score": 0.8,
                    },
                    {
                        "chunk_id": "33333333-3333-3333-3333-333333333333",
                        "document_name": "025-pikachu.md",
                        "content": "...",
                        "similarity_score": 0.7,
                    },
                ],
            },
        )

    with _make_client_with_handler(httpx.MockTransport(handler)) as client:
        docs = client.search("dummy", top_k=5)

    assert docs == ["025-pikachu.md", "001-bulbizarre.md", "025-pikachu.md"]


def test_search_forwards_body() -> None:
    """Search sends query, top_k, and similarity_threshold in the JSON body."""
    captured: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        """
        Capture the JSON body and return an empty result payload.

        Parameters
        ----------
        request : httpx.Request
            The intercepted HTTP request whose body is recorded into
            the enclosing ``captured`` dict.

        Returns
        -------
        httpx.Response
            A fake response with zero results.
        """
        import json

        captured.update(json.loads(request.content))
        return httpx.Response(
            200,
            json={
                "query": "q",
                "total_results": 0,
                "embedding_time_ms": 0.0,
                "search_time_ms": 0.0,
                "results": [],
            },
        )

    with _make_client_with_handler(httpx.MockTransport(handler)) as client:
        client.search("q", top_k=7, similarity_threshold=0.25)

    assert captured == {"query": "q", "top_k": 7, "similarity_threshold": 0.25}


def test_search_raises_on_http_error() -> None:
    """A 500 response is raised as an HTTPStatusError."""

    def handler(_: httpx.Request) -> httpx.Response:
        """
        Return a 500 to exercise the error path.

        Parameters
        ----------
        _ : httpx.Request
            Unused; always responds 500.

        Returns
        -------
        httpx.Response
            A 500 Internal Server Error response.
        """
        return httpx.Response(500, text="boom")

    with _make_client_with_handler(httpx.MockTransport(handler)) as client:
        with pytest.raises(httpx.HTTPStatusError):
            client.search("q", top_k=5)
