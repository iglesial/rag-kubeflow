"""Application module for rag-loader."""

import json
from pathlib import Path

from lib_schemas.schemas import ChunkInput

from rag_loader.chunker import chunk_text
from rag_loader.reader import read_documents
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

        docs = read_documents(task_inputs.input_dir)
        print(f"Read {len(docs)} documents")

        all_chunks: list[ChunkInput] = []
        for doc in docs:
            text_chunks = chunk_text(
                str(doc["content"]),
                chunk_size=task_inputs.chunk_size,
                chunk_overlap=task_inputs.chunk_overlap,
            )
            raw_meta = doc.get("metadata")
            meta = {k: str(v) for k, v in raw_meta.items()} if isinstance(raw_meta, dict) else {}
            for i, content in enumerate(text_chunks):
                all_chunks.append(
                    ChunkInput(
                        document_name=str(doc["document_name"]),
                        chunk_index=i,
                        content=content,
                        metadata=meta,
                    )
                )

        print(f"Generated {len(all_chunks)} chunks")

        output_path = Path(task_inputs.output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        output_file = output_path / "chunks.json"
        output_file.write_text(
            json.dumps([c.model_dump() for c in all_chunks], indent=2),
            encoding="utf-8",
        )
        print(f"Saved chunks to {output_file}")
