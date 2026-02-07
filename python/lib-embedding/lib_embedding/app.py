"""Application module for lib-embedding."""

from lib_embedding.task_inputs import task_inputs


class App:
    """Diagnostic tool for embedding client library."""

    def run(self) -> None:
        """
        Run diagnostics.

        Load the embedding model and print its configuration.
        """
        print(f"Embedding model: {task_inputs.embedding_model}")
        print(f"Vector dimension: {task_inputs.vector_dim}")
