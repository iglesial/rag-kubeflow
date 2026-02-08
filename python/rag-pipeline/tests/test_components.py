"""Tests for KFP component definitions."""

from rag_pipeline.components.embedder import EMBEDDER_IMAGE, embedder_component
from rag_pipeline.components.loader import LOADER_IMAGE, loader_component


def test_loader_component_importable() -> None:
    """Test that loader_component can be imported without errors."""
    assert callable(loader_component)


def test_loader_image() -> None:
    """Test that loader component uses correct image."""
    assert LOADER_IMAGE == "rag-loader:latest"


def test_embedder_component_importable() -> None:
    """Test that embedder_component can be imported without errors."""
    assert callable(embedder_component)


def test_embedder_image() -> None:
    """Test that embedder component uses correct image."""
    assert EMBEDDER_IMAGE == "rag-embedder:latest"


def test_loader_component_has_pipeline_channel() -> None:
    """Test that loader_component is a valid KFP component."""
    assert hasattr(loader_component, "pipeline_func")


def test_embedder_component_has_pipeline_channel() -> None:
    """Test that embedder_component is a valid KFP component."""
    assert hasattr(embedder_component, "pipeline_func")
