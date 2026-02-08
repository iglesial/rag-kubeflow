"""KFP component definition for rag-embedder."""

from kfp import dsl

EMBEDDER_IMAGE = "rag-embedder:latest"


@dsl.container_component  # type: ignore[untyped-decorator]
def embedder_component(
    chunks_artifact: dsl.Input[dsl.Artifact],  # noqa: B008
    db_url: str,
    embedding_model: str,
    batch_size: int,
    embeddings_artifact: dsl.Output[dsl.Artifact],  # noqa: B008
) -> dsl.ContainerSpec:
    """
    Embed chunks and write to pgvector.

    Reads chunk JSON from the input artifact, generates embeddings,
    saves them to the output artifact, and writes to the database.

    Parameters
    ----------
    chunks_artifact : dsl.Input[dsl.Artifact]
        Input artifact containing chunk JSON files.
    db_url : str
        Database connection URL.
    embedding_model : str
        Name of the sentence-transformers model.
    batch_size : int
        Number of chunks to embed per batch.
    embeddings_artifact : dsl.Output[dsl.Artifact]
        Output artifact for embedding JSON files.

    Returns
    -------
    dsl.ContainerSpec
        Container specification for the embedder component.
    """
    return dsl.ContainerSpec(
        image=EMBEDDER_IMAGE,
        command=["python", "-m", "rag_embedder.main"],
        args=[
            "--input_dir",
            chunks_artifact.path,
            "--output_dir",
            embeddings_artifact.path,
            "--db_url",
            db_url,
            "--embedding_model",
            embedding_model,
            "--batch_size",
            str(batch_size),
        ],
    )
