"""Application module for rag-embedder."""

from rag_embedder.task_inputs import task_inputs


class App:
    """Batch embedding application for RAG system."""

    def run(self) -> None:
        """
        Run the batch embedder.

        Read chunks from ``input_dir``, embed them, and store in the database.
        """
        print(f"Input directory:   {task_inputs.input_dir}")
        print(f"Database URL:      {task_inputs.db_url}")
        print(f"Embedding model:   {task_inputs.embedding_model}")
        print(f"Batch size:        {task_inputs.batch_size}")
        print("rag-embedder: OK")
