"""KFP component definition for rag-loader."""

from kfp import dsl

LOADER_IMAGE = "rag-loader:latest"


@dsl.container_component  # type: ignore[untyped-decorator]
def loader_component(
    input_dir: str,
    chunk_size: int,
    chunk_overlap: int,
    chunks_artifact: dsl.Output[dsl.Artifact],  # noqa: B008
) -> dsl.ContainerSpec:
    """
    Load and chunk documents from input directory.

    Reads documents, splits them into chunks, and writes chunk JSON
    to the output artifact path.

    Parameters
    ----------
    input_dir : str
        Directory containing input documents.
    chunk_size : int
        Maximum number of characters per chunk.
    chunk_overlap : int
        Number of overlapping characters between consecutive chunks.
    chunks_artifact : dsl.Output[dsl.Artifact]
        Output artifact for chunk JSON files.

    Returns
    -------
    dsl.ContainerSpec
        Container specification for the loader component.
    """
    return dsl.ContainerSpec(
        image=LOADER_IMAGE,
        command=["python", "-m", "rag_loader.main"],
        args=[
            "--input_dir",
            input_dir,
            "--output_dir",
            chunks_artifact.path,
            "--chunk_size",
            str(chunk_size),
            "--chunk_overlap",
            str(chunk_overlap),
        ],
    )
