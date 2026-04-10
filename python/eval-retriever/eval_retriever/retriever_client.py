"""Thin synchronous HTTP client for the rag-retriever search endpoint."""

import httpx


class RetrieverClient:
    """
    Synchronous HTTP client for the rag-retriever ``/search`` endpoint.

    Parameters
    ----------
    base_url : str
        Base URL of the rag-retriever service, e.g. ``http://localhost:8000``.
    timeout_s : float
        Per-request HTTP timeout in seconds.
    """

    def __init__(self, base_url: str, timeout_s: float = 30.0) -> None:
        """
        Initialize the retriever client.

        Parameters
        ----------
        base_url : str
            Base URL of the rag-retriever service.
        timeout_s : float
            Per-request HTTP timeout in seconds.
        """
        self._client = httpx.Client(base_url=base_url, timeout=timeout_s)

    def search(
        self,
        query: str,
        top_k: int,
        similarity_threshold: float = 0.0,
    ) -> list[str]:
        """
        Query the retriever and return the ranked list of document names.

        Parameters
        ----------
        query : str
            The search query.
        top_k : int
            Number of chunks to request.
        similarity_threshold : float
            Minimum cosine similarity for returned chunks.

        Returns
        -------
        list[str]
            Document filenames in the order returned by the retriever
            (highest-scoring first). The same document may appear multiple
            times if several of its chunks match.

        Raises
        ------
        httpx.HTTPError
            On network failure or non-2xx response.
        """
        response = self._client.post(
            "/search",
            json={
                "query": query,
                "top_k": top_k,
                "similarity_threshold": similarity_threshold,
            },
        )
        response.raise_for_status()
        payload = response.json()
        results = payload.get("results", [])
        return [result["document_name"] for result in results]

    def close(self) -> None:
        """Close the underlying HTTP connection pool."""
        self._client.close()

    def __enter__(self) -> "RetrieverClient":
        """
        Enter the context manager.

        Returns
        -------
        RetrieverClient
            This client instance.
        """
        return self

    def __exit__(self, *_: object) -> None:
        """
        Close the client on context-manager exit.

        Parameters
        ----------
        *_ : object
            Exception type, value, and traceback forwarded by ``with``.
            Ignored — the client is always closed regardless of errors.
        """
        self.close()
