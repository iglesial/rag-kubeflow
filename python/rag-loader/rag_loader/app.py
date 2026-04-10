"""Application module for rag-loader."""

import json
import re
from pathlib import Path

from lib_schemas.schemas import ChunkInput

from rag_loader.chunker import chunk_text
from rag_loader.reader import read_documents
from rag_loader.task_inputs import task_inputs

_POKEMON_NAME_RE = re.compile(r"^\d+-(.+?)\.(?:md|txt)$", re.IGNORECASE)


def _extract_pokemon_name(document_name: str) -> str:
    """
    Extract the Pokémon name from a document filename.

    Expects filenames of the form ``NNN-name.md`` (e.g. ``025-pikachu.md``).
    Falls back to the filename stem if the pattern does not match.

    Parameters
    ----------
    document_name : str
        The document filename, e.g. ``"025-pikachu.md"``.

    Returns
    -------
    str
        The extracted name (e.g. ``"pikachu"``), or the filename stem if no
        numeric prefix is found.
    """
    match = _POKEMON_NAME_RE.match(document_name)
    if match:
        return match.group(1)
    return Path(document_name).stem


class App:
    """Document loader application for RAG system."""

    def run(self) -> None:
        """
        Run the document loader.

        Read documents from ``input_dir``, chunk them, and write JSON to ``output_dir``.
        """
        print(f"Input directory:      {task_inputs.input_dir}")
        print(f"Output directory:     {task_inputs.output_dir}")
        print(f"Chunk size:           {task_inputs.chunk_size}")
        print(f"Chunk overlap:        {task_inputs.chunk_overlap}")
        print(f"Inject document name: {task_inputs.inject_document_name}")

        docs = read_documents(task_inputs.input_dir)
        print(f"Read {len(docs)} documents")

        all_chunks: list[ChunkInput] = []
        for doc in docs:
            document_name = str(doc["document_name"])
            text_chunks = chunk_text(
                str(doc["content"]),
                chunk_size=task_inputs.chunk_size,
                chunk_overlap=task_inputs.chunk_overlap,
            )
            raw_meta = doc.get("metadata")
            meta = {k: str(v) for k, v in raw_meta.items()} if isinstance(raw_meta, dict) else {}

            pokemon_name = _extract_pokemon_name(document_name)
            meta["pokemon_name"] = pokemon_name

            for i, content in enumerate(text_chunks):
                final_content = (
                    f"Pokémon: {pokemon_name}\n\n{content}"
                    if task_inputs.inject_document_name
                    else content
                )
                all_chunks.append(
                    ChunkInput(
                        document_name=document_name,
                        chunk_index=i,
                        content=final_content,
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
