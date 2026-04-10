"""Tests for embedding client."""

import sys
import types
from unittest.mock import MagicMock

import pytest

from lib_embedding.embedding import EmbeddingClient, _load_sentence_transformer

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


def test_load_hub_model_does_not_touch_mlflow(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Test that loading a Hub name routes through ``SentenceTransformer`` only.

    Parameters
    ----------
    monkeypatch : pytest.MonkeyPatch
        Pytest monkeypatch fixture.
    """
    called: dict[str, str] = {}

    def fake_st(name: str) -> object:
        """
        Record the name argument and return a dummy model.

        Parameters
        ----------
        name : str
            The model name passed by the loader.

        Returns
        -------
        object
            A sentinel dummy model.
        """
        called["name"] = name
        return object()

    monkeypatch.setattr("lib_embedding.embedding.SentenceTransformer", fake_st)
    _load_sentence_transformer("all-MiniLM-L6-v2")
    assert called == {"name": "all-MiniLM-L6-v2"}


def test_load_mlflow_uri_routes_through_mlflow(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Test that a ``models:/`` URI is loaded via ``mlflow.sentence_transformers``.

    Fakes the ``mlflow.sentence_transformers`` module in ``sys.modules`` so
    tests do not require ``mlflow`` to be installed.

    Parameters
    ----------
    monkeypatch : pytest.MonkeyPatch
        Pytest monkeypatch fixture.
    """
    fake_model = object()
    load_model_mock = MagicMock(return_value=fake_model)

    fake_mlflow = types.ModuleType("mlflow")
    fake_mlflow_st = types.ModuleType("mlflow.sentence_transformers")
    fake_mlflow_st.load_model = load_model_mock  # type: ignore[attr-defined]
    fake_mlflow.sentence_transformers = fake_mlflow_st  # type: ignore[attr-defined]

    monkeypatch.setitem(sys.modules, "mlflow", fake_mlflow)
    monkeypatch.setitem(sys.modules, "mlflow.sentence_transformers", fake_mlflow_st)

    # Guard: the bare SentenceTransformer must NOT be called for an MLFlow URI.
    def fail_st(_name: str) -> object:
        """
        Fail loudly if SentenceTransformer is called for a models:/ URI.

        Parameters
        ----------
        _name : str
            Unused, only present to match the real signature.

        Returns
        -------
        object
            Never returns — always raises.

        Raises
        ------
        AssertionError
            Always, to flag that this path should not have been taken.
        """
        raise AssertionError("SentenceTransformer should not be called for models:/ URIs")

    monkeypatch.setattr("lib_embedding.embedding.SentenceTransformer", fail_st)

    result = _load_sentence_transformer("models:/rag-embedder@candidate")

    assert result is fake_model
    load_model_mock.assert_called_once_with("models:/rag-embedder@candidate")


def test_load_mlflow_uri_missing_mlflow_raises_import_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Test that a clear ImportError is raised if ``mlflow`` is not installed.

    Parameters
    ----------
    monkeypatch : pytest.MonkeyPatch
        Pytest monkeypatch fixture.
    """
    # Remove any previously-loaded mlflow modules from sys.modules, then install
    # a finder that raises ImportError on mlflow imports.
    for name in list(sys.modules):
        if name == "mlflow" or name.startswith("mlflow."):
            monkeypatch.delitem(sys.modules, name, raising=False)

    real_import = __builtins__["__import__"] if isinstance(__builtins__, dict) else __import__  # type: ignore[index]

    def fake_import(name: str, *args: object, **kwargs: object) -> object:
        """
        Raise ImportError on any mlflow import, otherwise defer to the real import.

        Parameters
        ----------
        name : str
            The module name being imported.
        *args : object
            Passed through to the real importer.
        **kwargs : object
            Passed through to the real importer.

        Returns
        -------
        object
            The module returned by the real importer, for non-mlflow names.

        Raises
        ------
        ImportError
            When ``name`` starts with ``mlflow``.
        """
        if name == "mlflow.sentence_transformers" or name.startswith("mlflow"):
            raise ImportError("No module named 'mlflow'")
        return real_import(name, *args, **kwargs)  # type: ignore[operator]

    monkeypatch.setattr("builtins.__import__", fake_import)

    with pytest.raises(ImportError, match="mlflow is required"):
        _load_sentence_transformer("models:/rag-embedder@candidate")
