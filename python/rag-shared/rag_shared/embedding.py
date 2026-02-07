"""Embedding client wrapping sentence-transformers."""

from sentence_transformers import SentenceTransformer


class EmbeddingClient:
    """
    Client for generating text embeddings using sentence-transformers.

    Parameters
    ----------
    model_name : str
        Name of the sentence-transformers model to load.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        """
        Initialize the embedding client.

        Parameters
        ----------
        model_name : str
            Name of the sentence-transformers model to load.
        """
        self._model = SentenceTransformer(model_name)

    def encode(self, texts: list[str], batch_size: int = 32) -> list[list[float]]:
        """
        Encode texts into embedding vectors.

        Parameters
        ----------
        texts : list[str]
            List of texts to encode.
        batch_size : int
            Batch size for encoding.

        Returns
        -------
        list[list[float]]
            List of embedding vectors.
        """
        if not texts:
            return []
        embeddings = self._model.encode(texts, batch_size=batch_size)
        return [vec.tolist() for vec in embeddings]

    @property
    def dimension(self) -> int:
        """
        Return the embedding dimension.

        Returns
        -------
        int
            Dimension of the embedding vectors.
        """
        return self._model.get_sentence_embedding_dimension()  # type: ignore[return-value]
