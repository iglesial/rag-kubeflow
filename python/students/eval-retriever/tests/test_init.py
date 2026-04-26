"""Smoke test for the package import surface."""

import eval_retriever


def test_version_exists() -> None:
    """The package exposes a ``__version__`` string."""
    assert isinstance(eval_retriever.__version__, str)
    assert eval_retriever.__version__  # non-empty
