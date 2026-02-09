"""Kubeflow Pipeline definition for RAG ingestion."""

from kfp import dsl

from rag_pipeline.components.embedder import embedder_component
from rag_pipeline.components.loader import loader_component


@dsl.pipeline(name="rag-ingestion", description="Load, chunk, embed, and store documents")  # type: ignore[untyped-decorator]
def rag_ingestion_pipeline(
    input_dir: str = "/data/documents",
    chunk_size: int = 512,
    chunk_overlap: int = 64,
    db_url: str = "postgresql+asyncpg://rag:rag@host.docker.internal:5432/rag",
    embedding_model: str = "all-MiniLM-L6-v2",
    batch_size: int = 32,
) -> None:
    """
    RAG ingestion pipeline: loader -> embedder.

    Chains the document loader and embedding components so that the
    loader output artifact feeds into the embedder input.

    Parameters
    ----------
    input_dir : str
        Directory containing input documents (baked into the loader image).
    chunk_size : int
        Maximum number of characters per chunk.
    chunk_overlap : int
        Number of overlapping characters between consecutive chunks.
    db_url : str
        Database connection URL.
    embedding_model : str
        Name of the sentence-transformers model.
    batch_size : int
        Number of chunks to embed per batch.
    """
    loader_task = loader_component(
        input_dir=input_dir,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    embedder_component(
        chunks_artifact=loader_task.outputs["chunks_artifact"],
        db_url=db_url,
        embedding_model=embedding_model,
        batch_size=batch_size,
    )
