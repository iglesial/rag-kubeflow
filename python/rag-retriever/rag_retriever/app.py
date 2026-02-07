"""Application module for rag-retriever."""

from rag_retriever.task_inputs import task_inputs


class App:
    """FastAPI retrieval service application."""

    def run(self) -> None:
        """
        Run the retrieval API server.

        Starts a uvicorn server with the FastAPI application on the
        configured host and port.
        """
        print(f"Host:            {task_inputs.host}")
        print(f"Port:            {task_inputs.port}")
        print(f"Database URL:    {task_inputs.db_url}")
        print(f"Embedding model: {task_inputs.embedding_model}")
        print(f"Default top_k:   {task_inputs.top_k}")
        print("rag-retriever: server not yet implemented")
