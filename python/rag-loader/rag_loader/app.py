"""Application module for rag-loader."""

from rag_loader.task_inputs import task_inputs


class App:
    """Document loader application for RAG system."""

    def run(self) -> None:
        """
        Run the document loader.

        Read documents from ``input_dir``, chunk them, and write JSON to ``output_dir``.
        """
        print(f"Input directory:  {task_inputs.input_dir}")
        print(f"Output directory: {task_inputs.output_dir}")
        print(f"Chunk size:       {task_inputs.chunk_size}")
        print(f"Chunk overlap:    {task_inputs.chunk_overlap}")
        print("rag-loader: OK")
