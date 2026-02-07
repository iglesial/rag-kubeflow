"""Application module for lib-embedding."""

from lib_embedding.embedding import EmbeddingClient
from lib_embedding.task_inputs import task_inputs


class App:
    """Diagnostic tool for embedding client library."""

    def run(self) -> None:
        """
        Run diagnostics.

        Load the embedding model and print its name and dimension.
        """
        model_name = task_inputs.embedding_model
        print(f"Loading model: {model_name}")
        client = EmbeddingClient(model_name)
        print(f"Model: {model_name} ({client.dimension} dims)")
