"""Tests for pipeline definition and compilation."""

import os
from pathlib import Path

from kfp import compiler

from rag_pipeline.pipeline import rag_ingestion_pipeline


def test_pipeline_compiles(tmp_path: Path) -> None:
    """
    Test that the pipeline compiles to valid YAML.

    Parameters
    ----------
    tmp_path : Path
        Pytest temporary directory fixture.
    """
    output_path = str(tmp_path / "pipeline.yaml")
    compiler.Compiler().compile(
        pipeline_func=rag_ingestion_pipeline,
        package_path=output_path,
    )
    assert os.path.exists(output_path)
    content = Path(output_path).read_text(encoding="utf-8")
    assert len(content) > 0


def test_pipeline_yaml_contains_components(tmp_path: Path) -> None:
    """
    Test that compiled YAML contains both loader and embedder components.

    Parameters
    ----------
    tmp_path : Path
        Pytest temporary directory fixture.
    """
    output_path = str(tmp_path / "pipeline.yaml")
    compiler.Compiler().compile(
        pipeline_func=rag_ingestion_pipeline,
        package_path=output_path,
    )
    content = Path(output_path).read_text(encoding="utf-8")
    assert "loader-component" in content
    assert "embedder-component" in content


def test_pipeline_yaml_has_parameters(tmp_path: Path) -> None:
    """
    Test that compiled YAML contains expected pipeline parameters.

    Parameters
    ----------
    tmp_path : Path
        Pytest temporary directory fixture.
    """
    output_path = str(tmp_path / "pipeline.yaml")
    compiler.Compiler().compile(
        pipeline_func=rag_ingestion_pipeline,
        package_path=output_path,
    )
    content = Path(output_path).read_text(encoding="utf-8")
    assert "input_dir" in content
    assert "chunk_size" in content
    assert "db_url" in content
    assert "embedding_model" in content
    assert "batch_size" in content


def test_pipeline_embedder_depends_on_loader(tmp_path: Path) -> None:
    """
    Test that the embedder task depends on the loader task output.

    Parameters
    ----------
    tmp_path : Path
        Pytest temporary directory fixture.
    """
    output_path = str(tmp_path / "pipeline.yaml")
    compiler.Compiler().compile(
        pipeline_func=rag_ingestion_pipeline,
        package_path=output_path,
    )
    content = Path(output_path).read_text(encoding="utf-8")
    # The embedder should reference loader's output artifact
    assert "chunks_artifact" in content


def test_pipeline_is_callable() -> None:
    """Test that rag_ingestion_pipeline is a valid KFP pipeline."""
    assert hasattr(rag_ingestion_pipeline, "pipeline_func")
