"""Application module for rag-embedder."""

import asyncio
import json
from pathlib import Path

from lib_embedding.embedding import EmbeddingClient
from lib_orm.db import get_async_session
from lib_schemas.schemas import ChunkInput, ChunkWithEmbedding

from rag_embedder.task_inputs import task_inputs
from rag_embedder.writer import write_chunks


class App:
    """Batch embedding application for RAG system."""

    def run(self) -> None:
        """
        Run the batch embedder.

        Read chunks from ``input_dir``, embed them, save to ``output_dir``,
        and optionally write to the database.
        """
        print(f"Input directory:   {task_inputs.input_dir}")
        print(f"Output directory:  {task_inputs.output_dir}")
        print(f"Database URL:      {task_inputs.db_url}")
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

        # Write to database
        asyncio.run(self._write_to_db(results))

    @staticmethod
    async def _write_to_db(results: list[ChunkWithEmbedding]) -> None:
        """
        Write embeddings to the database.

        Parameters
        ----------
        results : list[ChunkWithEmbedding]
            Chunks with embeddings to persist.
        """
        try:
            async with get_async_session(task_inputs.db_url) as session:
                count = await write_chunks(session, results)
            print(f"Wrote {count} rows to database")
        except Exception as exc:  # noqa: BLE001
            print(f"DB write skipped: {exc}")
