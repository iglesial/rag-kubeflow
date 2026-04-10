"""Embedding client wrapping sentence-transformers."""

from sentence_transformers import SentenceTransformer

_MLFLOW_URI_PREFIX = "models:/"


def _load_sentence_transformer(model_name_or_uri: str) -> SentenceTransformer:
    """
    Load a ``SentenceTransformer`` from a Hub name, local path, or MLFlow URI.

    Routes to ``mlflow.sentence_transformers.load_model`` when the input
    starts with ``models:/`` (e.g. ``models:/rag-embedder@candidate``),
    otherwise loads via ``sentence_transformers.SentenceTransformer`` directly.

    Parameters
    ----------
    model_name_or_uri : str
        Hugging Face model name, local path, or MLFlow registered-model URI.

    Returns
    -------
    SentenceTransformer
        The loaded model.

    Raises
    ------
    ImportError
        If an MLFlow URI is requested but the ``mlflow`` package is not installed.
    """
    if model_name_or_uri.startswith(_MLFLOW_URI_PREFIX):
        try:
            import mlflow.sentence_transformers as mlflow_st
        except ImportError as exc:  # pragma: no cover - guard for missing optional dep
            msg = (
                f"mlflow is required to load '{model_name_or_uri}'. "
                "Install the optional extra: `pip install lib-embedding[mlflow]`."
            )
            raise ImportError(msg) from exc
        return mlflow_st.load_model(model_name_or_uri)  # type: ignore[no-any-return]
    return SentenceTransformer(model_name_or_uri)


class EmbeddingClient:
    """
    Client for generating text embeddings using sentence-transformers.

    Parameters
    ----------
    model_name : str
        Name of the sentence-transformers model to load, a local path, or an
        MLFlow registered-model URI of the form ``models:/<name>@<alias>`` or
        ``models:/<name>/<version>``.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        """
        Initialize the embedding client.

        Parameters
        ----------
        model_name : str
            Hugging Face model name, local path, or MLFlow URI
            (``models:/<name>@<alias>``).
        """
        self._model = _load_sentence_transformer(model_name)

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
