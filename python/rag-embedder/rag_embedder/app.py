"""Application module for rag-embedder."""

import json
from pathlib import Path

from lib_embedding.embedding import EmbeddingClient
from lib_schemas.schemas import ChunkInput, ChunkWithEmbedding

from rag_embedder.task_inputs import task_inputs


class App:
    """Batch embedding application for RAG system."""

    def run(self) -> None:
        """
        Run the batch embedder.

        Read chunks from ``input_dir``, embed them, and save to ``output_dir``.
        """
        print(f"Input directory:   {task_inputs.input_dir}")
        print(f"Output directory:  {task_inputs.output_dir}")
        print(f"Embedding model:   {task_inputs.embedding_model}")
        print(f"Batch size:        {task_inputs.batch_size}")

        # Load chunks
        input_path = Path(task_inputs.input_dir)
        chunks: list[ChunkInput] = []
        for json_file in sorted(input_path.glob("*.json")):
            data = json.loads(json_file.read_text(encoding="utf-8"))
            if isinstance(data, list):
                chunks.extend(ChunkInput(**item) for item in data)
        print(f"Loaded {len(chunks)} chunks")

        if not chunks:
            print("No chunks to embed")
            return

        # Embed
        client = EmbeddingClient(task_inputs.embedding_model)
        print(f"Model loaded: {task_inputs.embedding_model} ({client.dimension} dims)")

        texts = [c.content for c in chunks]
        embeddings = client.encode(texts, batch_size=task_inputs.batch_size)
        print(f"Embedded {len(embeddings)} chunks")

        # Build output
        results = [
            ChunkWithEmbedding(**chunk.model_dump(), embedding=emb)
            for chunk, emb in zip(chunks, embeddings, strict=True)
        ]

        # Save to output dir
        output_path = Path(task_inputs.output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        output_file = output_path / "embeddings.json"
        output_file.write_text(
            json.dumps([r.model_dump() for r in results], indent=2),
            encoding="utf-8",
        )
        print(f"Saved {len(results)} embeddings to {output_file}")
